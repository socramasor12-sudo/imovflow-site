#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publicar.py v2.1 - Marcos Rosa Negocios Imobiliarios
Pipeline unificado de publicacao imobiliaria.

Etapas:
  1. Carrega JSON (aceita V4 nested e V5 flat)
  2. VALIDA dados (titulo, slug, valor, etc.)
  3. VALIDA fotos (minimo 3, foto_capa existe em disco)
  4. Checa DUPLICATA no WordPress
  5. Mostra RESUMO visual + pede confirmacao
  6. Otimiza fotos (redimensiona 1920px + watermark + JPEG 82)
  7. Upload via REST API
  8. Cria post CPT 'imovel'
  9. PHP fix (meta fields + post_parent + thumbnails)
  10. Limpa cache LiteSpeed
  11. Cria nota Obsidian
  12. Move pasta para _publicados
  13. Abre URL

Uso:
    python publicar.py <slug>
    python publicar.py <slug> --dry-run    # so valida, nao publica
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
# HELPERS (ASCII puro)
# ============================================================
def info(msg):  print(f"  [INFO] {msg}")
def ok(msg):    print(f"  [OK]   {msg}")
def warn(msg):  print(f"  [!]    {msg}")
def err(msg):   print(f"  [ERRO] {msg}"); sys.exit(1)

def step(n, total, msg):
    print()
    print(f"[{n}/{total}] {msg}")
    print("-" * 60)

def confirma(pergunta):
    return input(f"\n>> {pergunta} (s/N): ").strip().lower() == 's'

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
    """Inicia logging duplo (tela + arquivo). Chamar no inicio do main()."""
    global _LOG_FILE, _LOG_PATH
    pasta_logs = PASTA_SCRIPTS / "logs"
    pasta_logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    sufixo = "-dryrun" if is_dry_run else ""
    _LOG_PATH = pasta_logs / f"publicar-{slug}-{stamp}{sufixo}.log"
    _LOG_FILE = open(_LOG_PATH, "w", encoding="utf-8", errors="replace")
    # Header do log (so no arquivo, nao na tela)
    _LOG_FILE.write(f"# publicar.py log\n")
    _LOG_FILE.write(f"# slug:      {slug}\n")
    _LOG_FILE.write(f"# mode:      {'DRY-RUN' if is_dry_run else 'PRODUCAO'}\n")
    _LOG_FILE.write(f"# start:     {datetime.now().isoformat()}\n")
    _LOG_FILE.write(f"# argv:      {sys.argv}\n")
    _LOG_FILE.write("=" * 60 + "\n\n")
    _LOG_FILE.flush()
    # Tee stdout/stderr
    sys.stdout = _Tee(sys.stdout, _LOG_FILE)
    sys.stderr = _Tee(sys.stderr, _LOG_FILE)
    atexit.register(close_logging)

def close_logging():
    """Fecha o arquivo de log. Registrado via atexit."""
    global _LOG_FILE
    if _LOG_FILE:
        try:
            _LOG_FILE.write(f"\n# end: {datetime.now().isoformat()}\n")
            _LOG_FILE.flush()
            _LOG_FILE.close()
        except Exception:
            pass
        _LOG_FILE = None

def fmt_valor(v):
    try:
        return f"R$ {int(float(v)):,}".replace(',', '.')
    except Exception:
        return f"R$ {v}"

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
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except json.JSONDecodeError as e:
        err(f"JSON invalido: {e}")
    except Exception as e:
        err(f"Erro lendo JSON: {e}")

    # V4 (formulario) -> V5 (flat)
    if 'imovel' in dados:
        info("Convertendo V4 (nested) -> V5 (flat)...")
        i   = dados['imovel']
        cla = i.get('classificacao', {})
        inf = i.get('informacoes_basicas', {})
        seo = i.get('seo', {})
        dados = {
            'titulo':          inf.get('titulo', ''),
            'slug':            inf.get('slug', ''),
            'tipo':            cla.get('tipo', ''),
            'finalidade':      cla.get('finalidade', 'venda'),
            'valor':           inf.get('valor', 0),
            'area':            inf.get('area', 0),
            'quartos':         inf.get('quartos', 0),
            'banheiros':       inf.get('banheiros', 0),
            'vagas':           inf.get('vagas', 0),
            'bairro':          inf.get('bairro', ''),
            'cidade':          inf.get('cidade', 'Anapolis'),
            'estado':          inf.get('estado', 'GO'),
            'descricao':       i.get('descricao', ''),
            'seo_title':       seo.get('title', ''),
            'seo_description': seo.get('description', ''),
            'foto_capa':       i.get('foto_capa', ''),
            'parceiro':        i.get('parceiro', {})
        }
    return dados, arquivo

# ============================================================
# VALIDACAO DE DADOS
# ============================================================
def validar_dados(dados, slug):
    erros = []
    obrigatorios = ['titulo', 'tipo', 'finalidade', 'valor', 'area',
                    'bairro', 'cidade', 'estado', 'descricao']
    for campo in obrigatorios:
        if not dados.get(campo):
            erros.append(f"Campo obrigatorio vazio: '{campo}'")

    # Titulo parece slug?
    titulo = str(dados.get('titulo', ''))
    if titulo and titulo.count('-') > 3 and ' ' not in titulo:
        erros.append(f"Titulo parece slug (sem espacos): '{titulo}'")

    # Slug do JSON diverge do argumento?
    slug_json = dados.get('slug', '')
    if slug_json and slug_json != slug:
        erros.append(
            f"Slug diverge:\n"
            f"       JSON:      '{slug_json}'\n"
            f"       Argumento: '{slug}'"
        )

    # Valor razoavel?
    try:
        valor = float(dados.get('valor', 0))
        if valor < 10000:
            erros.append(f"Valor muito baixo ({fmt_valor(valor)}) - parece erro")
        if valor > 10_000_000:
            erros.append(f"Valor muito alto ({fmt_valor(valor)}) - parece erro")
    except (ValueError, TypeError):
        erros.append(f"Valor nao e numero: '{dados.get('valor')}'")

    return erros

# ============================================================
# VALIDACAO DE FOTOS (impede publicar com fotos faltando)
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

    if foto_capa:
        capa_norm = foto_capa.lower().replace(' ', '').replace('-', '').replace('_', '')
        tem_capa = any(
            capa_norm in f.stem.lower().replace(' ', '').replace('-', '').replace('_', '')
            for f in fotos
        )
        if not tem_capa:
            erros.append(
                f"foto_capa='{foto_capa}' nao encontrada em disco\n"
                f"       Fotos: {[f.name for f in fotos]}"
            )

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
# OTIMIZAR FOTOS (inline - nao depende de otimizador externo)
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

            # converte para RGB (HEIC, PNG, RGBA -> JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                fundo = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                mask = img.split()[-1] if img.mode == 'RGBA' else None
                fundo.paste(img, mask=mask)
                img = fundo
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # redimensiona
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)

            # watermark (15% da largura, canto inferior direito)
            if wm:
                wm_w = int(img.width * 0.15)
                wm_h = int(wm.height * (wm_w / wm.width))
                wm_r = wm.resize((wm_w, wm_h), Image.LANCZOS)
                img_rgba = img.convert('RGBA')
                pos = (img.width - wm_w - 20, img.height - wm_h - 20)
                img_rgba.paste(wm_r, pos, wm_r)
                img = img_rgba.convert('RGB')

            nome = foto.stem.lower().replace(' ', '-') + '.jpg'
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

    atts = [capa_id] + [g for g in galeria_ids if g != capa_id]
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

    # Upload via base64 | base64 -d over SSH (shell=True, compativel Windows)
    b64 = base64.b64encode(script.encode('utf-8')).decode('ascii')
    nome = f"mrfix-{post_id}.php"
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no {SSH_HOST} "echo {b64} | base64 -d > ~/www/{nome}"'
    r = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        warn(f"Upload PHP falhou (rc={r.returncode}): {r.stderr[:300]}")
        return False

    # Valida que o arquivo chegou ao servidor
    check_cmd = f'ssh -o StrictHostKeyChecking=no {SSH_HOST} "ls -la ~/www/{nome}"'
    r2 = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=30)
    if r2.returncode != 0 or nome not in r2.stdout:
        warn(f"PHP nao chegou no servidor: {r2.stdout[:200]}")
        return False
    info(f"  PHP uploaded: {r2.stdout.strip()}")

    # Executa
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
# MAIN
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Uso: python publicar.py <slug> [--dry-run]")
        sys.exit(1)

    slug    = sys.argv[1].strip()
    dry_run = "--dry-run" in sys.argv

    setup_logging(slug, dry_run)

    print()
    print("=" * 60)
    print(f"  PUBLICAR: {slug}" + ("  [DRY-RUN]" if dry_run else ""))
    print("=" * 60)

    pasta_imovel = PASTA_CAPTACAO / slug
    if not pasta_imovel.exists():
        err(f"Pasta nao existe: {pasta_imovel}\n"
            f"       Rode antes:  python iniciar_imovel.py {slug}")

    pasta_originais = pasta_imovel / "fotos-originais"
    pasta_prontas   = pasta_imovel / "fotos-prontas"

    # ===== 1. JSON =====
    step(1, 8, "Carregando JSON")
    dados, arq_json = carregar_json(pasta_imovel)
    if not dados.get('slug'):
        dados['slug'] = slug
    ok(f"JSON: {arq_json.name}")

    # Normalizar finalidade: sempre "Venda" ou "Aluguel"
    _fin = str(dados.get('finalidade', '')).strip().lower()
    if _fin in ('venda', 'vender', 'sale', 'v'):
        dados['finalidade'] = 'Venda'
    elif _fin in ('aluguel', 'aluguer', 'rent', 'alugar', 'a'):
        dados['finalidade'] = 'Aluguel'
    elif _fin:
        warn(f"Finalidade desconhecida: '{_fin}' - mantendo como esta")

    # ===== 2. Validar dados =====
    step(2, 8, "Validando dados do JSON")
    erros = validar_dados(dados, slug)
    if erros:
        print("\n  [ABORTADO] Problemas no JSON:")
        for e in erros:
            print(f"    - {e}")
        sys.exit(1)
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
    step(4, 8, "Checando duplicata no WordPress")
    dup_id = ja_existe_no_wp(slug)
    if dup_id:
        print(f"\n  [ABORTADO] Ja existe post com slug '{slug}' (ID {dup_id})")
        print(f"    Veja: {WP_URL}/wp-admin/post.php?post={dup_id}&action=edit")
        sys.exit(1)
    ok("Slug disponivel")

    # ===== 5. Resumo =====
    print()
    print("=" * 60)
    print("  RESUMO")
    print("=" * 60)
    print(f"  Titulo:    {dados.get('titulo', '')}")
    print(f"  Slug:      {dados.get('slug', '')}")
    print(f"  Tipo:      {dados.get('tipo', '')} ({dados.get('finalidade', '')})")
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

    if not confirma("Publicar?"):
        print("\nCancelado.")
        sys.exit(0)

    # ===== 6. Otimizar =====
    step(5, 8, "Otimizando fotos")
    prontas = otimizar_fotos(pasta_originais, pasta_prontas)
    ok(f"{len(prontas)} foto(s) em fotos-prontas\\")

    # ===== 7. Upload =====
    step(6, 8, "Upload para WordPress")
    capa_id = None
    galeria = []
    capa_busca = dados.get('foto_capa', '').lower().replace(' ', '').replace('-', '').replace('_', '')

    for i, foto in enumerate(prontas, 1):
        att = upload_foto(foto)
        galeria.append(att)
        nome_norm = foto.stem.lower().replace('-', '').replace('_', '')
        marca = ""
        if capa_id is None and capa_busca and capa_busca in nome_norm:
            capa_id = att
            marca = "  [CAPA]"
        info(f"  [{i}/{len(prontas)}] {foto.name} -> ID {att}{marca}")

    if capa_id is None:
        capa_id = galeria[0]
        info(f"  (capa nao matcheada, usando primeira: ID {capa_id})")

    # ===== 8. Criar post =====
    step(7, 8, "Criando post no WordPress")
    post = criar_post(dados, capa_id, galeria)
    post_id = post['id']
    url     = post.get('link', f"{WP_URL}/imovel/{slug}/")
    ok(f"Post ID {post_id}")

    info("Aplicando PHP fix (meta + post_parent + thumbs)...")
    fix_ok = php_fix(post_id, dados, capa_id, galeria)

    info("Limpando cache...")
    limpar_cache()

    if not fix_ok:
        print()
        print("=" * 60)
        print("  [!] PHP FIX FALHOU")
        print("  Post criado no WP, mas meta fields (preco, quartos,")
        print("  banheiros, vagas) provavelmente NAO foram gravados.")
        print(f"  Post ID: {post_id}")
        print(f"  Valide: {WP_URL}/imoveis/ (aba anonima)")
        print("  Se estiver errado, rode fix manual antes de seguir.")
        print("=" * 60)
        if not confirma("Continuar finalizacao (mover pasta, criar nota)?"):
            print("\n[ABORTADO] Post no WP mas pasta NAO movida.")
            print(f"Investigar post {post_id} antes de publicar outro.")
            sys.exit(1)

    # ===== 9. Finalizar =====
    step(8, 8, "Finalizando")
    try:
        criar_nota_obsidian(pasta_imovel, dados, post_id)
    except Exception as e:
        warn(f"Nota Obsidian: {e}")

    mover_para_publicados(pasta_imovel, slug)

    print()
    print("=" * 60)
    print(f"  PUBLICADO!")
    print(f"  ID:  {post_id}")
    print(f"  URL: {url}")
    print(f"  LOG: {_LOG_PATH}")
    print("=" * 60)
    try: webbrowser.open(url)
    except Exception: pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELADO]")
        sys.exit(1)
