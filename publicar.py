#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publicar.py v2.2 - Marcos Rosa Negocios Imobiliarios
Pipeline unificado de publicacao imobiliaria.

Sprint 2 (22/04/2026): atomicidade — manifest + resume + rollback
Bugfix: validar_dados retornava dict validado, nao lista de erros.

Etapas:
  1. Carrega JSON (V4 nested e V5 flat)
  2. Valida dados (Pydantic)
  3. Valida fotos (minimo 3, foto_capa existe)
  4. Checa duplicata no WordPress
  5. Mostra resumo + confirmacao
  6. Otimiza fotos (1920px + watermark + JPEG 82)
  7. Upload via REST API
  8. Cria post CPT 'imovel'
  9. PHP fix (meta fields + post_parent + thumbnails)
  10. Limpa cache LiteSpeed
  11. Cria nota Obsidian
  12. Move pasta para _publicados
  13. Abre URL

Uso:
    python publicar.py <slug>               # publica normalmente
    python publicar.py <slug> --dry-run     # so valida, nao publica
    python publicar.py <slug> --rollback    # desfaz ultima publicacao do slug
"""

import sys
import os
import json
import shutil
import subprocess
import webbrowser
import base64
from pathlib import Path
from datetime import datetime
import atexit

# ============================================================
# FIX ENCODING WINDOWS
# ============================================================
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
# IMPORTS EXTERNOS
# ============================================================
try:
    import requests
    from PIL import Image
except ImportError as e:
    print(f"[ERRO] Biblioteca faltando: {e}")
    print("Instale: pip install requests Pillow pillow-heif")
    sys.exit(1)

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass  # HEIC opcional

# ============================================================
# CONFIGURACAO
# ============================================================
BASE_DRIVE       = Path(r"G:\Meu Drive\MR-Imoveis\imoveis")
PASTA_CAPTACAO   = BASE_DRIVE / "_em-captacao"
PASTA_PUBLICADOS = BASE_DRIVE / "_publicados"
PASTA_SCRIPTS    = Path(r"C:\Users\socra\marcos-rosa-tema")
WATERMARK_PATH   = PASTA_SCRIPTS / "assets" / "watermark.png"

WP_URL   = "https://imovflow.com.br"
WP_USER  = "marcos_admin"
WP_PASS  = "JdGD SV7X zRSO Gxg1 Vd3T f6FO"
SSH_HOST = "imovflow@191.6.209.223"

UA      = "curl/8.0"              # KingHost bloqueia UA do Python
HEADERS = {"User-Agent": UA}
AUTH    = (WP_USER, WP_PASS)

MIN_FOTOS    = 3
MAX_WIDTH    = 1920
JPEG_QUALITY = 82

# ============================================================
# HELPERS
# ============================================================
def info(msg):  print(f"  [INFO] {msg}")
def ok(msg):    print(f"  [OK]   {msg}")
def warn(msg):  print(f"  [!]    {msg}")
def err(msg):   print(f"  [ERRO] {msg}"); sys.exit(1)

def step(n, total, msg):
    print()
    print(f"[{n}/{total}] {msg}")
    print("-" * 60)

def skip_step(msg):
    print()
    print(f"[SKIP] {msg}")
    print("-" * 60)

def confirma(pergunta):
    return input(f"\n>> {pergunta} (s/N): ").strip().lower() == 's'

def fmt_valor(v):
    try:
        return f"R$ {int(float(v)):,}".replace(',', '.')
    except Exception:
        return f"R$ {v}"

# ============================================================
# LOGGING PERSISTENTE
# ============================================================
class _Tee:
    """Duplica stdout/stderr para um arquivo de log."""
    def __init__(self, original, arquivo):
        self._original = original
        self._arquivo  = arquivo
    def write(self, s):
        self._original.write(s)
        try:
            self._arquivo.write(s)
            self._arquivo.flush()
        except Exception:
            pass
    def flush(self):
        try: self._original.flush()
        except Exception: pass
        try: self._arquivo.flush()
        except Exception: pass
    def __getattr__(self, name):
        return getattr(self._original, name)

_LOG_FILE = None
_LOG_PATH = None

def setup_logging(slug, is_dry_run=False):
    global _LOG_FILE, _LOG_PATH
    pasta_logs = PASTA_SCRIPTS / "logs"
    pasta_logs.mkdir(parents=True, exist_ok=True)
    stamp  = datetime.now().strftime("%Y%m%d-%H%M%S")
    sufixo = "-dryrun" if is_dry_run else ""
    _LOG_PATH = pasta_logs / f"publicar-{slug}-{stamp}{sufixo}.log"
    _LOG_FILE = open(_LOG_PATH, "w", encoding="utf-8", errors="replace")
    _LOG_FILE.write(f"# publicar.py v2.2 log\n")
    _LOG_FILE.write(f"# slug:  {slug}\n")
    _LOG_FILE.write(f"# mode:  {'DRY-RUN' if is_dry_run else 'PRODUCAO'}\n")
    _LOG_FILE.write(f"# start: {datetime.now().isoformat()}\n")
    _LOG_FILE.write(f"# argv:  {sys.argv}\n")
    _LOG_FILE.write("=" * 60 + "\n\n")
    _LOG_FILE.flush()
    sys.stdout = _Tee(sys.stdout, _LOG_FILE)
    sys.stderr = _Tee(sys.stderr, _LOG_FILE)
    atexit.register(close_logging)

def close_logging():
    global _LOG_FILE
    if _LOG_FILE:
        try:
            _LOG_FILE.write(f"\n# end: {datetime.now().isoformat()}\n")
            _LOG_FILE.flush()
            _LOG_FILE.close()
        except Exception:
            pass
        _LOG_FILE = None

# ============================================================
# MANIFEST — Sprint 2
# Rastreia progresso etapa a etapa para resume/rollback.
# Arquivo: logs/manifest-<slug>.json (um por slug, sobrescrito em
# nova execucao completa).
# ============================================================
MANIFEST_STEPS = [
    'fotos_otimizadas',
    'fotos_upload',
    'post_criado',
    'php_fix',
    'cache_limpo',
    'obsidian',
    'pasta_movida',
]

class Manifest:
    def __init__(self, slug, path):
        self.slug = slug
        self.path = Path(path)
        self.data = {
            'slug':         slug,
            'started_at':   datetime.now().isoformat(),
            'completed_at': None,
            'steps':        {s: False for s in MANIFEST_STEPS},
            'post_id':      None,
            'capa_id':      None,
            'galeria_ids':  [],
            'url':          None,
        }

    @staticmethod
    def _path(slug):
        return PASTA_SCRIPTS / "logs" / f"manifest-{slug}.json"

    @classmethod
    def existe(cls, slug):
        return cls._path(slug).exists()

    @classmethod
    def carregar(cls, slug):
        p = cls._path(slug)
        m = cls.__new__(cls)
        m.slug = slug
        m.path = p
        with open(p, 'r', encoding='utf-8') as f:
            m.data = json.load(f)
        return m

    @classmethod
    def novo(cls, slug):
        (PASTA_SCRIPTS / "logs").mkdir(parents=True, exist_ok=True)
        m = cls(slug, cls._path(slug))
        m.salvar()
        return m

    def salvar(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def checkpoint(self, step_name, **kwargs):
        """Marca etapa como concluida e persiste imediatamente."""
        self.data['steps'][step_name] = True
        for k, v in kwargs.items():
            self.data[k] = v
        self.salvar()

    def feito(self, step_name):
        return self.data['steps'].get(step_name, False)

    def completo(self):
        self.data['completed_at'] = datetime.now().isoformat()
        self.salvar()

    def resumo_texto(self):
        feitos    = [s for s in MANIFEST_STEPS if self.data['steps'].get(s)]
        pendentes = [s for s in MANIFEST_STEPS if not self.data['steps'].get(s)]
        return feitos, pendentes

# ============================================================
# ROLLBACK — Sprint 2
# Desfaz etapas concluidas com base no manifest.
# Ordem inversa: pasta -> obsidian -> post -> attachments.
# ============================================================
def executar_rollback(manifest):
    print()
    print("=" * 60)
    print("  ROLLBACK")
    print("=" * 60)
    slug = manifest.data['slug']

    # 1. Mover pasta de volta para _em-captacao
    if manifest.data['steps'].get('pasta_movida'):
        src = PASTA_PUBLICADOS / slug
        dst = PASTA_CAPTACAO   / slug
        if src.exists() and not dst.exists():
            try:
                shutil.move(str(src), str(dst))
                ok(f"Pasta movida de volta -> _em-captacao\\{slug}")
            except Exception as e:
                warn(f"Nao consegui mover pasta: {e}")
        else:
            warn("Pasta nao esta em _publicados ou destino ja existe — pulando")

    # 2. Deletar nota Obsidian
    if manifest.data['steps'].get('obsidian'):
        for base in [PASTA_PUBLICADOS, PASTA_CAPTACAO]:
            nota = base / slug / f"{slug}.md"
            if nota.exists():
                nota.unlink()
                ok(f"Nota Obsidian removida: {nota.name}")
                break

    # 3. Deletar post do WP (force=true pula a lixeira)
    post_id = manifest.data.get('post_id')
    if manifest.data['steps'].get('post_criado') and post_id:
        try:
            r = requests.delete(
                f"{WP_URL}/wp-json/wp/v2/imovel/{post_id}",
                params={"force": "true"},
                headers=HEADERS, auth=AUTH, timeout=30
            )
            if r.status_code in (200, 201):
                ok(f"Post {post_id} deletado do WP")
            else:
                warn(f"Delete post {post_id} falhou: {r.status_code} - {r.text[:200]}")
        except Exception as e:
            warn(f"Erro deletando post {post_id}: {e}")

    # 4. Deletar attachments (fotos enviadas ao WP)
    galeria = manifest.data.get('galeria_ids', [])
    if manifest.data['steps'].get('fotos_upload') and galeria:
        for att_id in galeria:
            try:
                r = requests.delete(
                    f"{WP_URL}/wp-json/wp/v2/media/{att_id}",
                    params={"force": "true"},
                    headers=HEADERS, auth=AUTH, timeout=30
                )
                if r.status_code in (200, 201):
                    ok(f"Attachment {att_id} deletado")
                else:
                    warn(f"Delete attachment {att_id}: {r.status_code}")
            except Exception as e:
                warn(f"Erro attachment {att_id}: {e}")

    # 5. Remover manifest
    try:
        manifest.path.unlink()
        ok("Manifest removido")
    except Exception as e:
        warn(f"Nao deletei manifest: {e}")

    print()
    print("  Rollback concluido.")
    print(f"  Pasta disponivel em _em-captacao\\{slug}")
    print()

# ============================================================
# CARREGAR E NORMALIZAR JSON (V4 nested -> V5 flat)
# ============================================================
def carregar_json(pasta):
    candidatos = list(pasta.glob("imovel-*.json"))
    if not candidatos:
        err(f"Nenhum 'imovel-*.json' em {pasta}")
    if len(candidatos) > 1:
        warn(f"Multiplos JSONs - usando: {candidatos[0].name}")

    arquivo = candidatos[0]
    try:
        with open(arquivo, 'r', encoding='utf-8-sig') as f:
            dados = json.load(f)
    except json.JSONDecodeError as e:
        err(f"JSON invalido: {e}")
    except Exception as e:
        err(f"Erro lendo JSON: {e}")

    from schema_imovel import normalizar_v4_para_v5
    slug_fb = pasta.name if hasattr(pasta, 'name') else ''
    dados = normalizar_v4_para_v5(dados, slug_fallback=slug_fb)
    return dados, arquivo

# ============================================================
# VALIDACAO DE DADOS
# BUGFIX v2.2: retorna dict validado (nao lista de erros).
# Chama sys.exit(1) internamente se invalido.
# ============================================================
def validar_dados(dados, slug):
    from schema_imovel import Imovel, formatar_erros
    from pydantic import ValidationError

    if not dados.get('slug'):
        dados['slug'] = slug

    if dados.get('slug') and dados['slug'] != slug:
        warn(
            f"Slug diverge (usando argumento da linha de comando):\n"
            f"       JSON:      '{dados['slug']}'\n"
            f"       Argumento: '{slug}'"
        )
        dados['slug'] = slug

    try:
        modelo = Imovel.model_validate(dados)
    except ValidationError as e:
        print("")
        print(formatar_erros(e))
        sys.exit(1)

    return modelo.model_dump()   # dict validado com defaults aplicados

# ============================================================
# VALIDACAO DE FOTOS
# ============================================================
def validar_fotos(pasta_originais, foto_capa):
    erros = []

    if not pasta_originais.exists():
        erros.append(f"Pasta nao existe: {pasta_originais}")
        return erros, []

    exts = ('.jpg', '.jpeg', '.png', '.heic', '.webp')
    fotos = sorted([
        f for f in pasta_originais.iterdir()
        if f.is_file() and f.suffix.lower() in exts
    ])

    if len(fotos) < MIN_FOTOS:
        erros.append(f"So {len(fotos)} foto(s) - minimo {MIN_FOTOS}")

    return erros, fotos

# ============================================================
# DUPLICATA
# ============================================================
def ja_existe_no_wp(slug):
    try:
        r = requests.get(
            f"{WP_URL}/wp-json/wp/v2/imovel",
            params={"slug": slug, "status": "publish,draft,pending"},
            headers=HEADERS, auth=AUTH, timeout=15
        )
        if r.status_code == 200:
            posts = r.json()
            if posts:
                return posts[0].get('id')
    except Exception as e:
        warn(f"Check duplicata falhou: {e}")
    return None

# ============================================================
# OTIMIZAR FOTOS
# ============================================================
def otimizar_fotos(pasta_originais, pasta_prontas):
    pasta_prontas.mkdir(parents=True, exist_ok=True)
    for f in pasta_prontas.glob("*"):
        try: f.unlink()
        except Exception: pass

    exts = ('.jpg', '.jpeg', '.png', '.heic', '.webp')
    fotos = sorted([
        f for f in pasta_originais.iterdir()
        if f.is_file() and f.suffix.lower() in exts
    ])

    wm = None
    if WATERMARK_PATH.exists():
        try:
            wm = Image.open(WATERMARK_PATH).convert("RGBA")
        except Exception as e:
            warn(f"Watermark nao abriu: {e}")
    else:
        warn(f"Watermark ausente: {WATERMARK_PATH}")

    prontas = []
    for i, foto in enumerate(fotos, 1):
        try:
            img = Image.open(foto)

            if img.mode in ('RGBA', 'LA', 'P'):
                fundo = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                mask = img.split()[-1] if img.mode == 'RGBA' else None
                fundo.paste(img, mask=mask)
                img = fundo
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)

            # watermark: 25% largura, centralizada, opacidade 55%
            if wm:
                wm_w = int(img.width * 0.35)
                wm_h = int(wm.height * (wm_w / wm.width))
                wm_r = wm.resize((wm_w, wm_h), Image.LANCZOS)
                if wm_r.mode != 'RGBA':
                    wm_r = wm_r.convert('RGBA')
                alpha = wm_r.split()[3].point(lambda p: int(p * 0.55))
                wm_r.putalpha(alpha)
                img_rgba = img.convert('RGBA')
                pos = ((img.width - wm_w) // 2, (img.height - wm_h) // 2)
                img_rgba.paste(wm_r, pos, wm_r)
                img = img_rgba.convert('RGB')

            nome  = foto.stem.lower().replace(' ', '-') + '.jpg'
            saida = pasta_prontas / nome
            img.save(saida, 'JPEG', quality=JPEG_QUALITY, optimize=True)
            prontas.append(saida)
            info(f"  [{i}/{len(fotos)}] {nome}")
        except Exception as e:
            warn(f"Erro em {foto.name}: {e}")

    return prontas

# ============================================================
# UPLOAD FOTO
# ============================================================
def upload_foto(arquivo):
    with open(arquivo, 'rb') as f:
        r = requests.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            headers={
                **HEADERS,
                "Content-Disposition": f'attachment; filename="{arquivo.name}"',
                "Content-Type": "image/jpeg"
            },
            data=f.read(),
            auth=AUTH, timeout=120
        )
    if r.status_code not in (200, 201):
        err(f"Upload {arquivo.name} falhou: {r.status_code} - {r.text[:200]}")
    return r.json()['id']

# ============================================================
# CRIAR POST
# ============================================================
def criar_post(dados, capa_id, galeria_ids):
    payload = {
        'title':          dados['titulo'],
        'slug':           dados['slug'],
        'content':        dados['descricao'],
        'status':         'publish',
        'featured_media': capa_id,
        'meta': {
            '_imovel_tipo':       str(dados.get('tipo', '')),
            '_imovel_finalidade': str(dados.get('finalidade', 'venda')),
            '_imovel_valor':      str(dados.get('valor', '')),
            '_imovel_area':       str(dados.get('area', '')),
            '_imovel_quartos':    str(dados.get('quartos', '')),
            '_imovel_banheiros':  str(dados.get('banheiros', '')),
            '_imovel_vagas':      str(dados.get('vagas', '')),
            '_imovel_bairro':     str(dados.get('bairro', '')),
            '_imovel_galeria':    ','.join(str(i) for i in galeria_ids),
        }
    }
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/imovel",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload, auth=AUTH, timeout=30
    )
    if r.status_code not in (200, 201):
        err(f"Criar post falhou: {r.status_code} - {r.text[:300]}")
    return r.json()

# ============================================================
# PHP FIX (meta fields + post_parent + thumbnails)
# ============================================================
def php_fix(post_id, dados, capa_id, galeria_ids):
    token = f"mr{post_id}{int(datetime.now().timestamp())}"

    meta = {
        '_imovel_tipo':       str(dados.get('tipo', '')),
        '_imovel_finalidade': str(dados.get('finalidade', 'venda')),
        '_imovel_valor':      str(dados.get('valor', '')),
        '_imovel_area':       str(dados.get('area', '')),
        '_imovel_quartos':    str(dados.get('quartos', '')),
        '_imovel_banheiros':  str(dados.get('banheiros', '')),
        '_imovel_vagas':      str(dados.get('vagas', '')),
        '_imovel_bairro':     str(dados.get('bairro', '')),
        '_imovel_galeria':    ','.join(str(i) for i in galeria_ids),
    }
    php_meta_lines = []
    for k, v in meta.items():
        v_safe = v.replace("'", "\\'")
        php_meta_lines.append(
            f"    delete_post_meta({post_id}, '{k}');\n"
            f"    update_post_meta({post_id}, '{k}', sanitize_text_field('{v_safe}'));\n"
            f"    $_v = get_post_meta({post_id}, '{k}', true);\n"
            f"    echo \"META {k} = $_v\\n\";"
        )
    php_meta = "\n".join(php_meta_lines)

    atts       = [capa_id] + [g for g in galeria_ids if g != capa_id]
    php_parent = "\n".join(
        f"    wp_update_post(array('ID' => {aid}, 'post_parent' => {post_id}));"
        for aid in atts
    )
    lista_ids = ",".join(str(i) for i in atts)

    script = f"""<?php
if (!isset($_GET['token']) || $_GET['token'] !== '{token}') {{
    http_response_code(403); exit('forbidden');
}}
require_once(__DIR__ . '/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');
header('Content-Type: text/plain; charset=utf-8');
echo "PHP Fix post {post_id}\\n";
{php_meta}
echo "Meta fields OK\\n";
{php_parent}
echo "post_parent OK\\n";
set_post_thumbnail({post_id}, {capa_id});
echo "Featured OK ({capa_id})\\n";
foreach (array({lista_ids}) as $aid) {{
    $file = get_attached_file($aid);
    if ($file && file_exists($file)) {{
        $m = wp_generate_attachment_metadata($aid, $file);
        wp_update_attachment_metadata($aid, $m);
    }}
}}
echo "Thumbnails OK\\n";
clean_post_cache({post_id});
wp_cache_flush();
if (class_exists('\\LiteSpeed\\Purge')) {{
    \\LiteSpeed\\Purge::purge_all();
    echo "LiteSpeed purge_all OK\\n";
}} elseif (function_exists('litespeed_purge_all')) {{
    litespeed_purge_all();
    echo "litespeed_purge_all OK\\n";
}} else {{
    echo "LiteSpeed plugin nao detectado (ok)\\n";
}}
echo "Object cache flush OK\\n";
unlink(__FILE__);
echo "Auto-delete OK\\n";
"""

    b64     = base64.b64encode(script.encode('utf-8')).decode('ascii')
    nome    = f"mrfix-{post_id}.php"
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no {SSH_HOST} "echo {b64} | base64 -d > ~/www/{nome}"'
    r = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        warn(f"Upload PHP falhou (rc={r.returncode}): {r.stderr[:300]}")
        return False

    check_cmd = f'ssh -o StrictHostKeyChecking=no {SSH_HOST} "ls -la ~/www/{nome}"'
    r2 = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=30)
    if r2.returncode != 0 or nome not in r2.stdout:
        warn(f"PHP nao chegou no servidor: {r2.stdout[:200]}")
        return False
    info(f"  PHP uploaded: {r2.stdout.strip()}")

    try:
        r = requests.get(f"{WP_URL}/{nome}?token={token}",
                         headers=HEADERS, timeout=90)
        if "OK" in r.text:
            for linha in r.text.strip().split("\n"):
                info(f"  {linha}")
            return True
        warn(f"PHP fix retornou: {r.text[:300]}")
        return False
    except Exception as e:
        warn(f"PHP fix request falhou: {e}")
        return False

# ============================================================
# CACHE CLEAR
# ============================================================
def limpar_cache():
    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', SSH_HOST,
           'rm -rf ~/www/wp-content/cache/* ; rm -rf ~/www/wp-content/litespeed/*']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        ok("Cache LiteSpeed limpo")
    else:
        warn(f"Cache nao limpou: {r.stderr[:200]}")

# ============================================================
# NOTA OBSIDIAN
# ============================================================
def criar_nota_obsidian(pasta_imovel, dados, post_id):
    slug = dados['slug']
    url  = f"{WP_URL}/imovel/{slug}/"
    hoje = datetime.now().strftime("%Y-%m-%d")
    desc = dados.get('descricao', '').replace('<p>', '').replace('</p>', '\n\n')

    nota = f"""---
tipo: imovel
slug: {slug}
post_id: {post_id}
url: {url}
publicado_em: {hoje}
valor: {dados.get('valor', '')}
tipo_imovel: {dados.get('tipo', '')}
bairro: {dados.get('bairro', '')}
quartos: {dados.get('quartos', '')}
status: publicado
---

# {dados.get('titulo', slug)}

- URL: [{url}]({url})
- Post ID: {post_id}
- Valor: {fmt_valor(dados.get('valor', 0))}
- Area: {dados.get('area', '')} m2
- Quartos: {dados.get('quartos', '')}
- Bairro: {dados.get('bairro', '')}

## Descricao

{desc}
"""
    arq = pasta_imovel / f"{slug}.md"
    arq.write_text(nota, encoding='utf-8')
    ok(f"Nota: {arq.name}")

# ============================================================
# MOVER PARA _publicados
# ============================================================
def mover_para_publicados(pasta_origem, slug):
    PASTA_PUBLICADOS.mkdir(parents=True, exist_ok=True)
    destino = PASTA_PUBLICADOS / slug
    if destino.exists():
        warn(f"Destino ja existe: {destino} - pasta NAO movida")
        return pasta_origem
    try:
        shutil.move(str(pasta_origem), str(destino))
        ok(f"Movido -> _publicados\\{slug}")
        return destino
    except Exception as e:
        warn(f"Nao movei: {e}")
        return pasta_origem

# ============================================================
# SELECAO DE FOTO CAPA
# ============================================================
def selecionar_foto_capa(fotos_prontas: list, foto_capa_json: str) -> str:
    import re as _re
    nomes = [f.name for f in fotos_prontas]
    if foto_capa_json:
        base = Path(foto_capa_json).stem
        for nome in nomes:
            if Path(nome).stem == base:
                return nome
        warn(f"foto_capa '{foto_capa_json}' nao encontrada — aplicando auto-selecao")
    for nome in nomes:
        if _re.match(r'^fachada', nome, _re.IGNORECASE):
            info(f"foto_capa auto-selecionada (fachada): {nome}")
            return nome
    fallback = sorted(nomes)[0]
    info(f"foto_capa auto-selecionada (1a alfabetica): {fallback}")
    return fallback


# ============================================================
# MAIN
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Uso: python publicar.py <slug> [--dry-run] [--rollback]")
        sys.exit(1)

    slug          = sys.argv[1].strip()
    dry_run       = "--dry-run"  in sys.argv
    rollback_mode = "--rollback" in sys.argv
    yes_mode      = "--yes" in sys.argv or "-y" in sys.argv

    setup_logging(slug, dry_run)

    # ===== MODO ROLLBACK =====
    if rollback_mode:
        if not Manifest.existe(slug):
            err(
                f"Nenhum manifest encontrado para '{slug}'.\n"
                f"       Esperado em: {Manifest._path(slug)}"
            )
        m = Manifest.carregar(slug)
        feitos, _ = m.resumo_texto()
        print()
        print("=" * 60)
        print(f"  ROLLBACK: {slug}")
        print(f"  Iniciado em: {m.data.get('started_at', '?')[:19]}")
        print(f"  Etapas feitas: {', '.join(feitos) or 'nenhuma'}")
        if m.data.get('post_id'):
            print(f"  Post ID: {m.data['post_id']}")
        print("=" * 60)
        if not confirma(f"Confirmar rollback de '{slug}'? (apaga post/fotos do WP)"):
            print("\nCancelado.")
            sys.exit(0)
        executar_rollback(m)
        sys.exit(0)

    # ===== CABECALHO =====
    print()
    print("=" * 60)
    print(f"  PUBLICAR: {slug}" + ("  [DRY-RUN]" if dry_run else ""))
    print("=" * 60)

    pasta_imovel    = PASTA_CAPTACAO / slug
    pasta_originais = pasta_imovel / "fotos-originais"
    pasta_prontas   = pasta_imovel / "fotos-prontas"

    if not pasta_imovel.exists():
        err(
            f"Pasta nao existe: {pasta_imovel}\n"
            f"       Rode antes:  python iniciar_imovel.py {slug}"
        )

    # ===== VERIFICAR MANIFEST EXISTENTE (resume/rollback interativo) =====
    retomando = False
    manifest  = None

    if Manifest.existe(slug):
        m_existing = Manifest.carregar(slug)

        if m_existing.data.get('completed_at'):
            # Publicacao anterior ja concluida — ignora manifest antigo
            warn("Manifest de publicacao anterior concluida encontrado — iniciando novo.")
            manifest = Manifest.novo(slug)
        else:
            feitos, pendentes = m_existing.resumo_texto()
            if not feitos:
                m_existing.path.unlink()
                info("Manifest anterior sem etapas — descartado, iniciando limpo")
            else:
                print()
                print("=" * 60)
                print("  [!] EXECUCAO INCOMPLETA DETECTADA")
                print(f"  Iniciado em:     {m_existing.data.get('started_at', '?')[:19]}")
                print(f"  Etapas feitas:   {', '.join(feitos) or 'nenhuma'}")
                print(f"  Etapas faltando: {', '.join(pendentes)}")
                if m_existing.data.get('post_id'):
                    print(f"  Post ID no WP:   {m_existing.data['post_id']}")
                print("=" * 60)
                print()
                print("  Opcoes:")
                print("  [R] Retomar de onde parou")
                print("  [Z] Rollback (apaga post/fotos do WP e limpa)")
                print("  [N] Cancelar")
                print()
                opcao = input(">> Escolha (R/Z/N): ").strip().upper()
                if opcao == 'Z':
                    executar_rollback(m_existing)
                    sys.exit(0)
                elif opcao == 'R':
                    retomando = True
                    manifest  = m_existing
                    print()
                    print("  Retomando execucao...")
                else:
                    print("\nCancelado.")
                    sys.exit(0)

    if manifest is None:
        manifest = Manifest.novo(slug)

    # ===== 1. JSON =====
    step(1, 8, "Carregando JSON")
    dados, arq_json = carregar_json(pasta_imovel)
    if not dados.get('slug'):
        dados['slug'] = slug
    ok(f"JSON: {arq_json.name}")

    # Normalizar finalidade
    _fin = str(dados.get('finalidade', '')).strip().lower()
    if _fin in ('venda', 'vender', 'sale', 'v'):
        dados['finalidade'] = 'Venda'
    elif _fin in ('aluguel', 'aluguer', 'rent', 'alugar', 'a'):
        dados['finalidade'] = 'Aluguel'
    elif _fin:
        warn(f"Finalidade desconhecida: '{_fin}' - mantendo como esta")

    # ===== 2. Validar dados =====
    # BUGFIX v2.2: dados = dict validado (sai com sys.exit se invalido)
    step(2, 8, "Validando dados do JSON")
    dados = validar_dados(dados, slug)
    ok("JSON valido")

    # ===== 3. Validar fotos =====
    step(3, 8, "Validando fotos em disco")
    erros_f, fotos = validar_fotos(pasta_originais, dados.get('foto_capa', ''))
    if erros_f:
        print("\n  [ABORTADO] Problemas nas fotos:")
        for e in erros_f:
            print(f"    - {e}")
        sys.exit(1)
    ok(f"{len(fotos)} foto(s)")

    # ===== 4. Duplicata =====
    # Pula se retomando e post ja foi criado (o proprio post e a duplicata)
    if not (retomando and manifest.feito('post_criado')):
        step(4, 8, "Checando duplicata no WordPress")
        dup_id = ja_existe_no_wp(slug)
        if dup_id:
            if retomando and dup_id == manifest.data.get('post_id'):
                ok(f"Post ja existe (ID {dup_id}) — retomada apos criacao do post")
            else:
                print(f"\n  [ABORTADO] Ja existe post com slug '{slug}' (ID {dup_id})")
                print(f"    Veja: {WP_URL}/wp-admin/post.php?post={dup_id}&action=edit")
                sys.exit(1)
        else:
            ok("Slug disponivel")
    else:
        skip_step("Checar duplicata (post ja criado no manifest)")

    # ===== 5. Resumo + confirmacao (pula se retomando) =====
    if not retomando:
        print()
        print("=" * 60)
        print("  RESUMO")
        print("=" * 60)
        print(f"  Titulo:    {dados.get('titulo', '')}")
        print(f"  Slug:      {dados.get('slug', '')}")
        print(f"  Tipo:      {dados.get('tipo', '')} ({dados.get('finalidade', '')})")
        print(f"  Negócio:   {dados.get('tipo_negocio', 'revendas')}")
        print(f"  Valor:     {fmt_valor(dados.get('valor', 0))}")
        print(f"  Area:      {dados.get('area', '')} m2")
        print(f"  Q/B/V:     {dados.get('quartos', '')}/{dados.get('banheiros', '')}/{dados.get('vagas', '')}")
        print(f"  Local:     {dados.get('bairro', '')}, {dados.get('cidade', '')}/{dados.get('estado', '')}")
        print(f"  Fotos:     {len(fotos)} ({', '.join(f.name for f in fotos[:3])}{'...' if len(fotos)>3 else ''})")
        print(f"  Capa:      '{dados.get('foto_capa', '(primeira)')}'")
        print("=" * 60)

        if dry_run:
            print(f"\n[DRY-RUN] Ok - nada publicado. Log: {_LOG_PATH}")
            sys.exit(0)

        if yes_mode:
            info("[--yes] Confirmacao pulada.")
        elif not confirma("Publicar?"):
            print("\nCancelado.")
            sys.exit(0)

    # ===== 6. Otimizar fotos =====
    if not manifest.feito('fotos_otimizadas'):
        step(5, 8, "Otimizando fotos")
        prontas = otimizar_fotos(pasta_originais, pasta_prontas)
        ok(f"{len(prontas)} foto(s) em fotos-prontas\\")
        manifest.checkpoint('fotos_otimizadas')
    else:
        skip_step("Otimizando fotos (ja feito)")
        exts_ok = ('.jpg', '.jpeg')
        prontas = sorted([
            f for f in pasta_prontas.iterdir()
            if f.is_file() and f.suffix.lower() in exts_ok
        ])
        ok(f"{len(prontas)} foto(s) recuperadas de fotos-prontas\\")

    # ===== 7. Upload =====
    if not manifest.feito('fotos_upload'):
        step(6, 8, "Upload para WordPress")
        capa_id    = None
        galeria    = []
        capa_nome  = selecionar_foto_capa(prontas, dados.get('foto_capa', ''))

        for i, foto in enumerate(prontas, 1):
            att       = upload_foto(foto)
            galeria.append(att)
            marca     = ""
            if capa_id is None and foto.name == capa_nome:
                capa_id = att
                marca   = "  [CAPA]"
            info(f"  [{i}/{len(prontas)}] {foto.name} -> ID {att}{marca}")

        if capa_id is None:
            capa_id = galeria[0]
            info(f"  (capa nao matcheada, usando primeira: ID {capa_id})")

        manifest.checkpoint('fotos_upload', capa_id=capa_id, galeria_ids=galeria)
    else:
        skip_step("Upload de fotos (ja feito)")
        capa_id = manifest.data['capa_id']
        galeria = manifest.data['galeria_ids']
        ok(f"capa_id={capa_id}  |  {len(galeria)} attachment(s) do manifest")

    # ===== 8. Criar post =====
    if not manifest.feito('post_criado'):
        step(7, 8, "Criando post no WordPress")
        post    = criar_post(dados, capa_id, galeria)
        post_id = post['id']
        url     = post.get('link', f"{WP_URL}/imovel/{slug}/")
        ok(f"Post ID {post_id}")
        manifest.checkpoint('post_criado', post_id=post_id, url=url)

        # ===== 8b. Atribuir taxonomia tipo_negocio =====
        tipo_neg = dados.get('tipo_negocio', 'revendas')
        try:
            # Resolver term_id pelo slug
            tr = requests.get(
                f"{WP_URL}/wp-json/wp/v2/tipo_negocio",
                params={"slug": tipo_neg},
                headers=HEADERS, auth=AUTH, timeout=15
            )
            if tr.status_code == 200 and tr.json():
                term_id = tr.json()[0]['id']
                # Atribuir ao post
                ar = requests.post(
                    f"{WP_URL}/wp-json/wp/v2/imovel/{post_id}",
                    headers={**HEADERS, "Content-Type": "application/json"},
                    json={"tipo_negocio": [term_id]},
                    auth=AUTH, timeout=15
                )
                if ar.status_code in (200, 201):
                    ok(f"Taxonomia tipo_negocio={tipo_neg} (term_id={term_id})")
                else:
                    warn(f"Atribuir taxonomia falhou: {ar.status_code} - {ar.text[:200]}")
            else:
                warn(f"Termo '{tipo_neg}' nao encontrado na API (status={tr.status_code})")
        except Exception as e:
            warn(f"Erro ao atribuir taxonomia: {e}")
    else:
        skip_step("Criar post (ja feito)")
        post_id = manifest.data['post_id']
        url     = manifest.data['url'] or f"{WP_URL}/imovel/{slug}/"
        ok(f"Post ID {post_id} recuperado do manifest")

    # ===== PHP Fix =====
    if not manifest.feito('php_fix'):
        info("Aplicando PHP fix (meta + post_parent + thumbs)...")
        fix_ok = php_fix(post_id, dados, capa_id, galeria)
        if fix_ok:
            manifest.checkpoint('php_fix')
        else:
            print()
            print("=" * 60)
            print("  [!] PHP FIX FALHOU")
            print("  Post criado, mas meta fields podem estar errados.")
            print(f"  Post ID: {post_id}")
            print(f"  Admin:   {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")
            print()
            print("  Para tentar novamente:")
            print(f"    python publicar.py {slug}            (retoma do php_fix)")
            print(f"    python publicar.py {slug} --rollback (apaga tudo)")
            print("=" * 60)
            if not confirma("Continuar mesmo assim (obsidian + mover pasta)?"):
                print(f"\n[ABORTADO] Post {post_id} no WP. Manifest salvo.")
                print(f"           Retome com:  python publicar.py {slug}")
                print(f"           Desfaca com: python publicar.py {slug} --rollback")
                sys.exit(1)
    else:
        skip_step("PHP fix (ja feito)")

    # ===== Cache =====
    if not manifest.feito('cache_limpo'):
        info("Limpando cache...")
        limpar_cache()
        manifest.checkpoint('cache_limpo')
    else:
        skip_step("Limpar cache (ja feito)")

    # ===== 9. Finalizar =====
    step(8, 8, "Finalizando")

    if not manifest.feito('obsidian'):
        try:
            criar_nota_obsidian(pasta_imovel, dados, post_id)
            manifest.checkpoint('obsidian')
        except Exception as e:
            warn(f"Nota Obsidian: {e}")
    else:
        skip_step("Nota Obsidian (ja feita)")

    if not manifest.feito('pasta_movida'):
        mover_para_publicados(pasta_imovel, slug)
        manifest.checkpoint('pasta_movida')
    else:
        skip_step("Mover pasta (ja feita)")

    manifest.completo()

    print()
    print("=" * 60)
    print(f"  PUBLICADO!")
    print(f"  ID:  {post_id}")
    print(f"  URL: {url}")
    print(f"  LOG: {_LOG_PATH}")
    print("=" * 60)
    try:
        webbrowser.open(url)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Manifest salvo.")
        print(f"            Retome com:  python publicar.py {sys.argv[1] if len(sys.argv) > 1 else '<slug>'}")
        sys.exit(1)
