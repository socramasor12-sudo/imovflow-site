# -*- coding: utf-8 -*-
"""
mr_crm.py — CRM de Leads com Match Inteligente
Marcos Rosa — Negócios Imobiliários | CRECI-GO 35088-F

Match em duas camadas:
  Camada 1: Critérios (bairro, tipo, preço, quartos) — SEMPRE funciona
  Camada 2: IA Gemini (refinamento) — opcional, se tiver chave

Uso:
    python mr_crm.py
    Acesse http://localhost:8080

Dependências:
    pip install flask requests
"""

import os, json, re, datetime, threading, webbrowser, base64, glob
from pathlib import Path
from flask import Flask, request, jsonify, Response
import requests as req

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
WP_BASE_URL    = "https://imovflow.com.br"
WP_USER        = "marcos_admin"
WP_APP_PASS    = "JdGD SV7X zRSO Gxg1 Vd3T f6FO"
OBSIDIAN_LEADS = Path(r"G:\Meu Drive\MR-Imoveis\leads")

WP_AUTH    = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
WP_HEADERS = {"User-Agent": "curl/8.0", "Authorization": f"Basic {WP_AUTH}"}

GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL   = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

app = Flask(__name__)

# ─── CACHE DE IMÓVEIS ────────────────────────────────────────────────────────
_cache_imoveis = {"data": [], "ts": 0}

def buscar_imoveis_wp(forcar=False):
    """Busca imóveis publicados no WordPress. Cache de 5 minutos."""
    import time
    agora = time.time()
    if not forcar and _cache_imoveis["data"] and (agora - _cache_imoveis["ts"]) < 300:
        return _cache_imoveis["data"]

    todos = []
    page = 1
    while True:
        try:
            r = req.get(
                f"{WP_BASE_URL}/wp-json/wp/v2/imovel?per_page=50&page={page}&status=publish",
                headers=WP_HEADERS, timeout=15
            )
            if r.status_code != 200:
                break
            lote = r.json()
            if not lote:
                break
            for p in lote:
                meta = p.get("meta", {})
                imovel = {
                    "id": p["id"],
                    "titulo": re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", "")),
                    "link": p.get("link", ""),
                    "tipo": meta.get("_imovel_tipo", ""),
                    "finalidade": meta.get("_imovel_finalidade", ""),
                    "valor": _parse_valor(meta.get("_imovel_valor", "0")),
                    "valor_fmt": meta.get("_imovel_valor", ""),
                    "area": meta.get("_imovel_area", ""),
                    "quartos": _parse_int(meta.get("_imovel_quartos", "0")),
                    "banheiros": _parse_int(meta.get("_imovel_banheiros", "0")),
                    "vagas": _parse_int(meta.get("_imovel_vagas", "0")),
                    "bairro": meta.get("_imovel_bairro", "").strip().lower(),
                    "descricao": re.sub(r'<[^>]+>', '', p.get("content", {}).get("rendered", ""))[:300],
                }
                todos.append(imovel)
            page += 1
        except Exception:
            break

    _cache_imoveis["data"] = todos
    _cache_imoveis["ts"] = agora
    return todos


def _parse_valor(v):
    """Converte string de valor para float. Ex: 'R$ 380.000,00' -> 380000"""
    if not v:
        return 0
    s = re.sub(r'[^\d,.]', '', str(v))
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return 0


def _parse_int(v):
    try:
        return int(re.sub(r'[^\d]', '', str(v)))
    except:
        return 0


# ─── OBSIDIAN: LER/SALVAR LEADS ──────────────────────────────────────────────
def ler_leads_obsidian():
    """Lê todos os leads da pasta Obsidian."""
    leads = []
    if not OBSIDIAN_LEADS.exists():
        return leads

    for arq in OBSIDIAN_LEADS.glob("*.md"):
        try:
            texto = arq.read_text(encoding="utf-8")
            front = _parse_frontmatter(texto)
            if front.get("tipo") != "lead":
                continue

            # Extrair seção "O que quer"
            oque_quer = ""
            historico = ""
            corpo = texto.split("---", 2)[-1] if texto.count("---") >= 2 else ""
            m_oq = re.search(r'##\s*O que quer\s*\n(.*?)(?=\n##|\Z)', corpo, re.DOTALL)
            if m_oq:
                oque_quer = m_oq.group(1).strip()
            m_hist = re.search(r'##\s*Hist[óo]rico\s*\n(.*?)(?=\n##|\Z)', corpo, re.DOTALL)
            if m_hist:
                historico = m_hist.group(1).strip()

            lead = {
                "arquivo": arq.name,
                "nome": front.get("nome", arq.stem),
                "tel": front.get("tel", ""),
                "via": front.get("via", ""),
                "recurso": front.get("recurso", ""),
                "status": front.get("status", "novo"),
                "prox": front.get("prox", ""),
                "oque_quer": oque_quer,
                "historico": historico,
            }
            leads.append(lead)
        except Exception:
            continue

    return leads


def _parse_frontmatter(texto):
    """Extrai frontmatter YAML simples."""
    m = re.match(r'^---\s*\n(.*?)\n---', texto, re.DOTALL)
    if not m:
        return {}
    dados = {}
    for linha in m.group(1).split("\n"):
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            dados[chave.strip()] = valor.strip()
    return dados


def salvar_lead_obsidian(nome, tel, via, recurso, oque_quer=""):
    """Salva lead como .md na pasta Obsidian."""
    OBSIDIAN_LEADS.mkdir(parents=True, exist_ok=True)
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    hoje_yaml = datetime.date.today().strftime("%Y-%m-%d")

    # Nome do arquivo seguro
    nome_arq = re.sub(r'[<>:"/\\|?*]', '', nome.strip())
    if not nome_arq:
        nome_arq = f"lead_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    caminho = OBSIDIAN_LEADS / f"{nome_arq}.md"

    # Se já existe, não sobrescrever
    if caminho.exists():
        return str(caminho), False

    conteudo = f"""---
tipo: lead
nome: {nome.strip()}
tel: {tel.strip()}
via: {via.strip()}
recurso: {recurso.strip()}
status: novo
prox: 
---

## O que quer
{oque_quer}

## Histórico
- {hoje} — Primeiro contato.
"""
    caminho.write_text(conteudo, encoding="utf-8")
    return str(caminho), True


# ─── MATCH POR CRITÉRIOS (CAMADA 1) ──────────────────────────────────────────
def extrair_criterios_lead(texto):
    """Extrai critérios de busca do texto do lead (linguagem natural)."""
    texto_lower = texto.lower()
    criterios = {
        "tipo": "",
        "bairro": "",
        "valor_max": 0,
        "quartos_min": 0,
    }

    # Tipo de imóvel
    tipos = {
        "casa": ["casa", "casinha", "sobrado"],
        "apartamento": ["apartamento", "apto", "ap", "apt"],
        "terreno": ["terreno", "lote", "chácara", "chacara", "fazenda", "rural", "sítio", "sitio"],
        "comercial": ["comercial", "sala", "loja", "galpão", "galpao", "ponto"],
    }
    for tipo, palavras in tipos.items():
        for p in palavras:
            if p in texto_lower:
                criterios["tipo"] = tipo
                break

    # Quartos
    m = re.search(r'(\d+)\s*(?:quarto|qto|qt|q\b|dormit)', texto_lower)
    if m:
        criterios["quartos_min"] = int(m.group(1))

    # Valor máximo
    m = re.search(r'(?:até|ate|max|máx|menos de|no máximo)\s*(?:r\$?\s*)?(\d[\d.,]*)\s*(mil|k|m)?', texto_lower)
    if m:
        val = float(m.group(1).replace('.', '').replace(',', '.'))
        mult = m.group(2)
        if mult in ('mil', 'k'):
            val *= 1000
        elif mult == 'm':
            val *= 1000000
        criterios["valor_max"] = val
    else:
        # Tentar padrão "400k", "400mil", "500.000"
        m2 = re.search(r'(\d[\d.,]*)\s*(mil|k)\b', texto_lower)
        if m2:
            val = float(m2.group(1).replace('.', '').replace(',', '.'))
            criterios["valor_max"] = val * 1000
        else:
            m3 = re.search(r'r\$?\s*(\d{2,3}(?:\.\d{3})+)', texto_lower)
            if m3:
                criterios["valor_max"] = float(m3.group(1).replace('.', ''))

    # Bairro — pega texto depois de "em ", "no ", "na ", "bairro "
    m = re.search(r'(?:em |no |na |bairro\s+)([a-záéíóúâêôãõç\s]+?)(?:\s*,|\s*-|\s+até|\s+com|\s+de\s+\d|\s*$)', texto_lower)
    if m:
        bairro = m.group(1).strip()
        # Remover palavras genéricas
        remove = ['anápolis', 'anapolis', 'goiânia', 'goiania', 'até', 'com', 'quartos']
        for r in remove:
            bairro = bairro.replace(r, '').strip()
        if len(bairro) > 2:
            criterios["bairro"] = bairro

    return criterios


def match_criterios(lead_texto, imoveis):
    """
    Match por critérios: compara texto do lead com imóveis do WP.
    Retorna lista de matches com score de 0 a 100.
    """
    criterios = extrair_criterios_lead(lead_texto)
    resultados = []

    for im in imoveis:
        score = 0
        motivos = []

        # Tipo (30 pontos)
        if criterios["tipo"]:
            if criterios["tipo"] in im["tipo"].lower():
                score += 30
                motivos.append(f"Tipo: {im['tipo']}")
            else:
                score -= 10
        else:
            score += 10  # sem filtro de tipo = neutro

        # Bairro (30 pontos)
        if criterios["bairro"]:
            bairro_im = im["bairro"].lower()
            bairro_lead = criterios["bairro"].lower()
            if bairro_lead in bairro_im or bairro_im in bairro_lead:
                score += 30
                motivos.append(f"Bairro: {im['bairro']}")
            else:
                score -= 5
        else:
            score += 10

        # Valor (25 pontos)
        if criterios["valor_max"] > 0 and im["valor"] > 0:
            if im["valor"] <= criterios["valor_max"]:
                score += 25
                motivos.append(f"Preço dentro da faixa")
            elif im["valor"] <= criterios["valor_max"] * 1.15:
                score += 10
                motivos.append(f"Preço 15% acima da faixa")
            else:
                score -= 10
                motivos.append(f"Preço acima da faixa")
        else:
            score += 10

        # Quartos (15 pontos)
        if criterios["quartos_min"] > 0 and im["quartos"] > 0:
            if im["quartos"] >= criterios["quartos_min"]:
                score += 15
                motivos.append(f"{im['quartos']} quartos")
            elif im["quartos"] == criterios["quartos_min"] - 1:
                score += 5
                motivos.append(f"{im['quartos']} quartos (1 a menos)")
        else:
            score += 5

        # Normalizar score para 0-100
        score = max(0, min(100, score))

        if score >= 25:
            resultados.append({
                "imovel_id": im["id"],
                "titulo": im["titulo"],
                "link": im["link"],
                "valor": im["valor_fmt"],
                "bairro": im["bairro"],
                "quartos": im["quartos"],
                "score": score,
                "motivos": motivos,
                "tipo_match": "criterios"
            })

    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados


# ─── MATCH POR IA — GEMINI (CAMADA 2, OPCIONAL) ──────────────────────────────
def chamar_gemini(prompt, api_key):
    """Chama Gemini e retorna texto. Retorna None se falhar."""
    try:
        r = req.post(
            f"{GEMINI_URL}?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if r.status_code != 200:
            return None
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


def match_ia(lead_texto, imoveis, api_key):
    """Match refinado por IA. Retorna lista ou None se falhar."""
    if not api_key:
        return None

    imoveis_txt = ""
    for im in imoveis:
        imoveis_txt += f"""
ID: {im['id']} | {im['titulo']}
Tipo: {im['tipo']} | Bairro: {im['bairro']} | Valor: {im['valor_fmt']}
Quartos: {im['quartos']} | Vagas: {im['vagas']} | Área: {im['area']}m²
{im['descricao']}
---"""

    prompt = f"""Você é um corretor de imóveis experiente.

LEAD:
{lead_texto}

IMÓVEIS DISPONÍVEIS:
{imoveis_txt}

Avalie a compatibilidade do lead com cada imóvel.
Considere: localização, tipo, preço, tamanho, perfil do comprador.

Retorne APENAS JSON válido, sem markdown, sem crases:
{{"matches":[{{"imovel_id":123,"score":85,"motivo":"Explicação curta"}}]}}

Inclua apenas imóveis com score >= 30. Ordene por score decrescente."""

    texto = chamar_gemini(prompt, api_key)
    if not texto:
        return None

    try:
        texto = re.sub(r'^```json\s*', '', texto.strip())
        texto = re.sub(r'\s*```$', '', texto)
        parsed = json.loads(texto)
        return parsed.get("matches", [])
    except:
        return None


def match_combinado(lead_texto, imoveis, api_key=""):
    """
    Match em duas camadas:
    1. Critérios (sempre funciona)
    2. IA Gemini (bônus, se disponível)
    Combina os scores quando a IA funciona.
    """
    # Camada 1 — sempre roda
    resultados_criterios = match_criterios(lead_texto, imoveis)

    # Camada 2 — tenta IA
    resultados_ia = match_ia(lead_texto, imoveis, api_key) if api_key else None

    if resultados_ia:
        # Combinar: média ponderada (criterios 40% + IA 60%)
        ia_dict = {m["imovel_id"]: m for m in resultados_ia}
        for r in resultados_criterios:
            ia_match = ia_dict.get(r["imovel_id"])
            if ia_match:
                r["score"] = int(r["score"] * 0.4 + ia_match["score"] * 0.6)
                r["motivos"].append(f"IA: {ia_match.get('motivo', '')}")
                r["tipo_match"] = "criterios + IA"

        # Adicionar matches que a IA encontrou mas critérios não
        ids_criterios = {r["imovel_id"] for r in resultados_criterios}
        for m in resultados_ia:
            if m["imovel_id"] not in ids_criterios:
                # Buscar dados do imóvel
                im = next((i for i in imoveis if i["id"] == m["imovel_id"]), None)
                if im:
                    resultados_criterios.append({
                        "imovel_id": im["id"],
                        "titulo": im["titulo"],
                        "link": im["link"],
                        "valor": im["valor_fmt"],
                        "bairro": im["bairro"],
                        "quartos": im["quartos"],
                        "score": m["score"],
                        "motivos": [f"IA: {m.get('motivo', '')}"],
                        "tipo_match": "IA"
                    })

        resultados_criterios.sort(key=lambda x: x["score"], reverse=True)

    return resultados_criterios, bool(resultados_ia)


# ─── ROTAS API ────────────────────────────────────────────────────────────────
@app.route("/api/imoveis")
def api_imoveis():
    forcar = request.args.get("forcar") == "1"
    imoveis = buscar_imoveis_wp(forcar)
    return jsonify({"ok": True, "total": len(imoveis), "imoveis": imoveis})


@app.route("/api/leads")
def api_leads():
    filtro = request.args.get("status", "")
    leads = ler_leads_obsidian()
    if filtro:
        leads = [l for l in leads if l["status"] == filtro]
    return jsonify({"ok": True, "total": len(leads), "leads": leads})


@app.route("/api/lead", methods=["POST"])
def api_salvar_lead():
    d = request.json or {}
    nome = d.get("nome", "").strip()
    tel = d.get("tel", "").strip()
    via = d.get("via", "").strip()
    recurso = d.get("recurso", "").strip()
    oque_quer = d.get("oque_quer", "").strip()

    if not nome:
        return jsonify({"ok": False, "erro": "Nome é obrigatório"})

    caminho, novo = salvar_lead_obsidian(nome, tel, via, recurso, oque_quer)
    if not novo:
        return jsonify({"ok": False, "erro": f"Lead '{nome}' já existe"})
    return jsonify({"ok": True, "arquivo": caminho})


@app.route("/api/match", methods=["POST"])
def api_match():
    d = request.json or {}
    texto = d.get("texto", "").strip()
    api_key = d.get("api_key", "").strip()

    if not texto:
        return jsonify({"ok": False, "erro": "Texto do lead é obrigatório"})

    imoveis = buscar_imoveis_wp()
    if not imoveis:
        return jsonify({"ok": False, "erro": "Nenhum imóvel publicado no site"})

    matches, usou_ia = match_combinado(texto, imoveis, api_key)
    return jsonify({
        "ok": True,
        "matches": matches,
        "usou_ia": usou_ia,
        "total_imoveis": len(imoveis)
    })


@app.route("/api/match-lote", methods=["POST"])
def api_match_lote():
    """Match em lote: cruza todos os leads novos com os imóveis."""
    d = request.json or {}
    api_key = d.get("api_key", "").strip()
    status_filtro = d.get("status", "novo")

    leads = ler_leads_obsidian()
    leads_filtrados = [l for l in leads if l["status"] == status_filtro]

    if not leads_filtrados:
        return jsonify({"ok": False, "erro": f"Nenhum lead com status '{status_filtro}'"})

    imoveis = buscar_imoveis_wp()
    if not imoveis:
        return jsonify({"ok": False, "erro": "Nenhum imóvel publicado no site"})

    resultados = []
    for lead in leads_filtrados:
        # Montar texto do lead para o match
        texto_lead = f"{lead['nome']}"
        if lead["oque_quer"]:
            texto_lead += f" {lead['oque_quer']}"
        if lead.get("historico"):
            texto_lead += f" {lead['historico']}"

        matches, usou_ia = match_combinado(texto_lead, imoveis, api_key)
        resultados.append({
            "lead": {
                "nome": lead["nome"],
                "tel": lead["tel"],
                "via": lead["via"],
                "recurso": lead["recurso"],
                "status": lead["status"],
            },
            "matches": matches[:3],  # Top 3 por lead
            "usou_ia": usou_ia
        })

    return jsonify({"ok": True, "resultados": resultados, "total_leads": len(leads_filtrados)})


@app.route("/api/lead-rapido", methods=["POST"])
def api_lead_rapido():
    """Cadastro rápido: texto natural → salva + match imediato."""
    d = request.json or {}
    texto = d.get("texto", "").strip()
    api_key = d.get("api_key", "").strip()

    if not texto:
        return jsonify({"ok": False, "erro": "Digite o lead"})

    # Extrair dados do texto natural
    dados = extrair_dados_natural(texto)

    # Salvar no Obsidian
    caminho, novo = salvar_lead_obsidian(
        dados["nome"], dados["tel"], dados["via"], dados["recurso"], dados["oque_quer"]
    )

    # Fazer match
    imoveis = buscar_imoveis_wp()
    matches = []
    usou_ia = False
    if imoveis:
        matches, usou_ia = match_combinado(texto, imoveis, api_key)

    return jsonify({
        "ok": True,
        "lead_novo": novo,
        "lead": dados,
        "matches": matches,
        "usou_ia": usou_ia
    })


def extrair_dados_natural(texto):
    """
    Extrai nome, telefone, via, recurso de texto natural.
    Ex: 'João Silva, 62991234567, financiamento aprovado, quer casa 3Q Jundiaí 400k'
    """
    dados = {"nome": "", "tel": "", "via": "", "recurso": "", "oque_quer": texto}

    # Telefone
    m = re.search(r'[\(]?\d{2}[\)]?\s*\d{4,5}[\-\s]?\d{4}', texto)
    if m:
        dados["tel"] = re.sub(r'[\s\-\(\)]', '', m.group())

    # Recurso
    texto_lower = texto.lower()
    if "aprovado" in texto_lower or "financiamento aprovado" in texto_lower:
        dados["recurso"] = "aprovado"
    elif "financiamento" in texto_lower or "financiar" in texto_lower:
        dados["recurso"] = "financiamento"
    elif "permuta" in texto_lower or "trocar" in texto_lower or "troca" in texto_lower:
        dados["recurso"] = "permuta"
    elif "próprio" in texto_lower or "proprio" in texto_lower or "vista" in texto_lower or "à vista" in texto_lower:
        dados["recurso"] = "proprio"

    # Nome — primeira parte antes de vírgula/telefone
    partes = re.split(r'[,;]', texto)
    if partes:
        possivel_nome = partes[0].strip()
        # Remover telefone do nome se presente
        possivel_nome = re.sub(r'[\(]?\d{2}[\)]?\s*\d{4,5}[\-\s]?\d{4}', '', possivel_nome).strip()
        # Se parece nome (2+ palavras, sem números)
        if possivel_nome and not re.search(r'\d', possivel_nome) and len(possivel_nome) > 2:
            dados["nome"] = possivel_nome
        elif not dados["nome"]:
            # Tentar primeira palavra como nome
            palavras = texto.split()
            if palavras and not re.search(r'\d', palavras[0]):
                dados["nome"] = palavras[0]

    return dados


# ─── INTERFACE HTML (MOBILE-FIRST) ───────────────────────────────────────────
@app.route("/")
def index():
    return Response(HTML_PAGE, content_type="text/html; charset=utf-8")


HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>MR CRM — Marcos Rosa</title>
<style>
:root {
    --azul: #1a2744;
    --dourado: #c9a84c;
    --verde: #27ae60;
    --vermelho: #e74c3c;
    --cinza-bg: #f5f5f5;
    --cinza-borda: #ddd;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--cinza-bg);
    color: #333;
    -webkit-text-size-adjust: 100%;
}
.header {
    background: var(--azul);
    color: white;
    padding: 16px;
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 100;
}
.header h1 { font-size: 18px; font-weight: 600; }
.header .sub { font-size: 12px; color: var(--dourado); margin-top: 4px; }
.status-bar {
    display: flex;
    gap: 8px;
    padding: 8px 16px;
    background: #fff;
    border-bottom: 1px solid var(--cinza-borda);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.status-pill {
    flex-shrink: 0;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid var(--cinza-borda);
    background: white;
    transition: all 0.2s;
}
.status-pill.active { background: var(--azul); color: white; border-color: var(--azul); }
.status-pill .count { 
    display: inline-block; 
    background: rgba(0,0,0,0.15); 
    border-radius: 10px; 
    padding: 1px 7px; 
    font-size: 11px; 
    margin-left: 4px; 
}
.tab-bar {
    display: flex;
    background: white;
    border-bottom: 2px solid var(--cinza-borda);
}
.tab {
    flex: 1;
    padding: 14px 8px;
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    color: #888;
    transition: all 0.2s;
}
.tab.active { color: var(--azul); border-bottom-color: var(--dourado); }
.panel { display: none; padding: 16px; }
.panel.active { display: block; }
.input-group { margin-bottom: 14px; }
.input-group label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #555;
    margin-bottom: 5px;
}
input[type="text"], input[type="tel"], textarea, select {
    width: 100%;
    padding: 14px;
    font-size: 16px;
    border: 2px solid var(--cinza-borda);
    border-radius: 10px;
    background: white;
    -webkit-appearance: none;
    transition: border-color 0.2s;
}
input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: var(--dourado);
}
textarea { min-height: 80px; resize: vertical; }
.btn {
    width: 100%;
    padding: 16px;
    font-size: 16px;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    margin-top: 8px;
    transition: opacity 0.2s;
}
.btn:active { opacity: 0.7; }
.btn-primary { background: var(--azul); color: white; }
.btn-success { background: var(--verde); color: white; }
.btn-gold { background: var(--dourado); color: var(--azul); }
.btn-danger { background: var(--vermelho); color: white; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.recurso-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 14px;
}
.recurso-opt {
    padding: 12px;
    text-align: center;
    border: 2px solid var(--cinza-borda);
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    background: white;
    transition: all 0.2s;
}
.recurso-opt.selected { border-color: var(--dourado); background: #fdf8ed; }
.recurso-opt .emoji { font-size: 20px; display: block; margin-bottom: 4px; }

.match-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid var(--cinza-borda);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.match-card.high { border-left-color: var(--verde); }
.match-card.medium { border-left-color: var(--dourado); }
.match-card.low { border-left-color: var(--vermelho); }
.match-score {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}
.match-score.high { background: var(--verde); }
.match-score.medium { background: var(--dourado); }
.match-score.low { background: var(--vermelho); }
.match-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.match-detail { font-size: 13px; color: #666; margin-bottom: 2px; }
.match-motivos { font-size: 12px; color: #888; margin-top: 6px; font-style: italic; }
.match-tipo { 
    display: inline-block;
    font-size: 11px; 
    padding: 2px 8px; 
    border-radius: 4px; 
    background: #eee; 
    color: #666;
    margin-top: 6px;
}

.lead-card {
    background: white;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.lead-info h3 { font-size: 15px; font-weight: 600; }
.lead-info p { font-size: 12px; color: #888; }
.lead-badge {
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}
.badge-aprovado { background: #d4edda; color: #155724; }
.badge-proprio { background: #d4edda; color: #155724; }
.badge-financiamento { background: #fff3cd; color: #856404; }
.badge-permuta { background: #d1ecf1; color: #0c5460; }

.resultado-box {
    margin-top: 16px;
    padding: 16px;
    background: white;
    border-radius: 12px;
}
.resultado-titulo {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--azul);
}

.config-box {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}
.config-box h3 { font-size: 14px; margin-bottom: 10px; color: var(--azul); }

.toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    border-radius: 10px;
    color: white;
    font-size: 14px;
    font-weight: 500;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s;
    max-width: 90%;
    text-align: center;
}
.toast.show { opacity: 1; }
.toast.ok { background: var(--verde); }
.toast.erro { background: var(--vermelho); }

.loading {
    display: none;
    text-align: center;
    padding: 20px;
    color: #888;
    font-size: 14px;
}
.loading.show { display: block; }

.vazio {
    text-align: center;
    padding: 40px 20px;
    color: #aaa;
    font-size: 14px;
}
.vazio .emoji { font-size: 40px; margin-bottom: 12px; }

.ia-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    margin-left: 8px;
}
.ia-on { background: #d4edda; color: #155724; }
.ia-off { background: #fff3cd; color: #856404; }

.lote-lead-grupo {
    margin-bottom: 20px;
    border-bottom: 1px solid var(--cinza-borda);
    padding-bottom: 16px;
}
.lote-lead-nome {
    font-size: 16px;
    font-weight: 700;
    color: var(--azul);
    margin-bottom: 4px;
}
.lote-lead-info {
    font-size: 12px;
    color: #888;
    margin-bottom: 10px;
}
</style>
</head>
<body>

<div class="header">
    <h1>Marcos Rosa — CRM</h1>
    <div class="sub" id="statusWP">Conectando ao WordPress...</div>
</div>

<!-- TABS -->
<div class="tab-bar">
    <div class="tab active" onclick="trocarTab('rapido')">⚡ Rápido</div>
    <div class="tab" onclick="trocarTab('leads')">👥 Leads</div>
    <div class="tab" onclick="trocarTab('match')">🔗 Match</div>
    <div class="tab" onclick="trocarTab('config')">⚙️</div>
</div>

<!-- ══════ ABA RÁPIDO ══════ -->
<div class="panel active" id="panel-rapido">
    <div class="input-group">
        <label>Cadastro rápido (texto natural)</label>
        <textarea id="textoRapido" placeholder="João Silva, 62991234567, financiamento aprovado, quer casa 3 quartos em Jundiaí até 400 mil" rows="3"></textarea>
    </div>
    <button class="btn btn-success" onclick="leadRapido()">⚡ Cadastrar + Match</button>

    <div class="loading" id="loadRapido">Processando...</div>

    <div id="resultRapido"></div>
</div>

<!-- ══════ ABA LEADS ══════ -->
<div class="panel" id="panel-leads">
    <h3 style="font-size:15px; margin-bottom:12px;">Novo Lead</h3>

    <div class="input-group">
        <label>Nome *</label>
        <input type="text" id="leadNome" placeholder="Nome do lead">
    </div>
    <div class="input-group">
        <label>Telefone</label>
        <input type="tel" id="leadTel" placeholder="62991234567">
    </div>
    <div class="input-group">
        <label>Via (de onde/quem veio)</label>
        <input type="text" id="leadVia" placeholder="Site, WhatsApp, João CRECI 12345...">
    </div>
    <div class="input-group">
        <label>Recurso</label>
        <div class="recurso-grid">
            <div class="recurso-opt" onclick="selRecurso(this,'financiamento')">
                <span class="emoji">🏦</span>Financiamento
            </div>
            <div class="recurso-opt" onclick="selRecurso(this,'aprovado')">
                <span class="emoji">✅</span>Aprovado
            </div>
            <div class="recurso-opt" onclick="selRecurso(this,'proprio')">
                <span class="emoji">💰</span>Próprio
            </div>
            <div class="recurso-opt" onclick="selRecurso(this,'permuta')">
                <span class="emoji">🔄</span>Permuta
            </div>
        </div>
    </div>
    <div class="input-group">
        <label>O que quer</label>
        <textarea id="leadOqueQuer" placeholder="Casa 3 quartos em Jundiaí até 400 mil"></textarea>
    </div>

    <button class="btn btn-primary" onclick="salvarLead()">💾 Salvar Lead</button>

    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">

    <h3 style="font-size:15px; margin-bottom:12px;">Leads Salvos</h3>
    <div class="status-bar" style="padding: 0; margin-bottom: 12px;">
        <div class="status-pill active" onclick="filtrarLeads('', this)">Todos</div>
        <div class="status-pill" onclick="filtrarLeads('novo', this)">Novos</div>
        <div class="status-pill" onclick="filtrarLeads('contactar', this)">Contactar</div>
        <div class="status-pill" onclick="filtrarLeads('negociando', this)">Negociando</div>
    </div>
    <div id="listaLeads"><div class="vazio"><div class="emoji">👥</div>Carregando leads...</div></div>
</div>

<!-- ══════ ABA MATCH ══════ -->
<div class="panel" id="panel-match">
    <div class="config-box">
        <h3>🔗 Match em Lote</h3>
        <p style="font-size:13px; color:#666; margin-bottom:12px;">
            Cruza todos os leads novos com os imóveis do site.
        </p>
        <button class="btn btn-gold" onclick="matchLote()">🔗 Match Todos os Novos</button>
    </div>

    <div class="loading" id="loadMatch">Cruzando leads com imóveis...</div>

    <div id="resultMatch"></div>
</div>

<!-- ══════ ABA CONFIG ══════ -->
<div class="panel" id="panel-config">
    <div class="config-box">
        <h3>🔑 Chave Gemini (opcional)</h3>
        <p style="font-size:12px; color:#888; margin-bottom:10px;">
            Sem chave = match por critérios (funciona sempre).<br>
            Com chave = match refinado por IA.
        </p>
        <div class="input-group">
            <input type="text" id="apiKey" placeholder="AIza..." value="">
        </div>
        <button class="btn btn-primary" onclick="salvarKey()">Salvar Chave</button>
    </div>

    <div class="config-box">
        <h3>📊 Status do Sistema</h3>
        <div id="sysStatus">Verificando...</div>
    </div>

    <div class="config-box">
        <h3>🔄 Cache</h3>
        <button class="btn btn-gold" onclick="recarregarImoveis()">Recarregar Imóveis do Site</button>
    </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ─── Estado ──────────────────────────────────────────────────────────────────
let apiKey = localStorage.getItem('gemini_key') || '';
let imoveis = [];
let leads = [];

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('apiKey').value = apiKey;
    carregarImoveis();
    carregarLeads();
});

// ─── Tabs ────────────────────────────────────────────────────────────────────
function trocarTab(nome) {
    document.querySelectorAll('.tab').forEach((t, i) => {
        t.classList.toggle('active', t.textContent.includes(
            nome === 'rapido' ? 'Rápido' :
            nome === 'leads' ? 'Leads' :
            nome === 'match' ? 'Match' : '⚙️'
        ));
    });
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById('panel-' + nome).classList.add('active');

    if (nome === 'leads') carregarLeads();
}

// ─── Toast ───────────────────────────────────────────────────────────────────
function toast(msg, tipo='ok') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast show ' + tipo;
    setTimeout(() => el.classList.remove('show'), 3000);
}

// ─── Imóveis ─────────────────────────────────────────────────────────────────
async function carregarImoveis(forcar=false) {
    try {
        const r = await fetch('/api/imoveis' + (forcar ? '?forcar=1' : ''));
        const d = await r.json();
        if (d.ok) {
            imoveis = d.imoveis;
            document.getElementById('statusWP').textContent =
                d.total + ' imóveis no site' + (apiKey ? ' | IA ativa' : ' | Match por critérios');
            atualizarSysStatus();
        }
    } catch(e) {
        document.getElementById('statusWP').textContent = 'Erro ao conectar WordPress';
    }
}

function recarregarImoveis() {
    carregarImoveis(true);
    toast('Imóveis recarregados');
}

// ─── Leads ───────────────────────────────────────────────────────────────────
async function carregarLeads(filtro='') {
    try {
        const url = '/api/leads' + (filtro ? '?status=' + filtro : '');
        const r = await fetch(url);
        const d = await r.json();
        if (d.ok) {
            leads = d.leads;
            renderLeads(leads);
        }
    } catch(e) {
        document.getElementById('listaLeads').innerHTML =
            '<div class="vazio"><div class="emoji">⚠️</div>Erro ao carregar leads</div>';
    }
}

function renderLeads(lista) {
    const el = document.getElementById('listaLeads');
    if (!lista.length) {
        el.innerHTML = '<div class="vazio"><div class="emoji">👥</div>Nenhum lead encontrado</div>';
        return;
    }
    el.innerHTML = lista.map(l => {
        let badge = '';
        if (l.recurso) {
            const cls = 'badge-' + l.recurso;
            const labels = {financiamento:'Financiamento', aprovado:'Aprovado ✓', proprio:'Próprio', permuta:'Permuta'};
            badge = '<span class="lead-badge ' + cls + '">' + (labels[l.recurso] || l.recurso) + '</span>';
        }
        return '<div class="lead-card">' +
            '<div class="lead-info">' +
                '<h3>' + esc(l.nome) + '</h3>' +
                '<p>' + esc(l.tel || 'sem tel') + ' · ' + esc(l.via || 'sem via') + '</p>' +
                (l.oque_quer ? '<p style="margin-top:4px;font-size:12px;color:#555">' + esc(l.oque_quer.substring(0,60)) + '</p>' : '') +
            '</div>' +
            badge +
        '</div>';
    }).join('');
}

function filtrarLeads(status, el) {
    document.querySelectorAll('.status-pill').forEach(p => p.classList.remove('active'));
    el.classList.add('active');
    carregarLeads(status);
}

// ─── Recurso ─────────────────────────────────────────────────────────────────
let recursoSelecionado = '';
function selRecurso(el, val) {
    document.querySelectorAll('.recurso-opt').forEach(o => o.classList.remove('selected'));
    if (recursoSelecionado === val) {
        recursoSelecionado = '';
    } else {
        el.classList.add('selected');
        recursoSelecionado = val;
    }
}

// ─── Salvar Lead ─────────────────────────────────────────────────────────────
async function salvarLead() {
    const nome = document.getElementById('leadNome').value.trim();
    if (!nome) { toast('Nome é obrigatório', 'erro'); return; }

    try {
        const r = await fetch('/api/lead', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                nome,
                tel: document.getElementById('leadTel').value.trim(),
                via: document.getElementById('leadVia').value.trim(),
                recurso: recursoSelecionado,
                oque_quer: document.getElementById('leadOqueQuer').value.trim()
            })
        });
        const d = await r.json();
        if (d.ok) {
            toast('Lead salvo!');
            document.getElementById('leadNome').value = '';
            document.getElementById('leadTel').value = '';
            document.getElementById('leadVia').value = '';
            document.getElementById('leadOqueQuer').value = '';
            recursoSelecionado = '';
            document.querySelectorAll('.recurso-opt').forEach(o => o.classList.remove('selected'));
            carregarLeads();
        } else {
            toast(d.erro, 'erro');
        }
    } catch(e) {
        toast('Erro ao salvar', 'erro');
    }
}

// ─── Lead Rápido ─────────────────────────────────────────────────────────────
async function leadRapido() {
    const texto = document.getElementById('textoRapido').value.trim();
    if (!texto) { toast('Digite o lead', 'erro'); return; }

    document.getElementById('loadRapido').classList.add('show');
    document.getElementById('resultRapido').innerHTML = '';

    try {
        const r = await fetch('/api/lead-rapido', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ texto, api_key: apiKey })
        });
        const d = await r.json();
        document.getElementById('loadRapido').classList.remove('show');

        if (d.ok) {
            let html = '<div class="resultado-box">';

            // Info do lead salvo
            if (d.lead_novo) {
                html += '<div style="background:#d4edda;padding:10px;border-radius:8px;margin-bottom:12px;font-size:13px">' +
                    '✅ Lead salvo: <strong>' + esc(d.lead.nome || 'sem nome') + '</strong>' +
                    (d.lead.recurso ? ' · ' + esc(d.lead.recurso) : '') +
                    '</div>';
            } else {
                html += '<div style="background:#fff3cd;padding:10px;border-radius:8px;margin-bottom:12px;font-size:13px">' +
                    '⚠️ Lead já existia: <strong>' + esc(d.lead.nome) + '</strong>' +
                    '</div>';
            }

            // Matches
            html += '<div class="resultado-titulo">Imóveis compatíveis ' +
                (d.usou_ia ? '<span class="ia-badge ia-on">IA ativa</span>' : '<span class="ia-badge ia-off">Critérios</span>') +
                '</div>';

            if (d.matches && d.matches.length) {
                html += renderMatches(d.matches);
            } else {
                html += '<div class="vazio"><div class="emoji">🏠</div>Nenhum imóvel compatível</div>';
            }
            html += '</div>';

            document.getElementById('resultRapido').innerHTML = html;
            document.getElementById('textoRapido').value = '';
            toast('Pronto!');
        } else {
            toast(d.erro, 'erro');
        }
    } catch(e) {
        document.getElementById('loadRapido').classList.remove('show');
        toast('Erro na conexão', 'erro');
    }
}

// ─── Match Lote ──────────────────────────────────────────────────────────────
async function matchLote() {
    document.getElementById('loadMatch').classList.add('show');
    document.getElementById('resultMatch').innerHTML = '';

    try {
        const r = await fetch('/api/match-lote', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ api_key: apiKey, status: 'novo' })
        });
        const d = await r.json();
        document.getElementById('loadMatch').classList.remove('show');

        if (d.ok) {
            let html = '<div class="resultado-box">';
            html += '<div class="resultado-titulo">' + d.total_leads + ' leads cruzados</div>';

            for (const item of d.resultados) {
                html += '<div class="lote-lead-grupo">';
                html += '<div class="lote-lead-nome">' + esc(item.lead.nome) + '</div>';
                html += '<div class="lote-lead-info">' +
                    esc(item.lead.tel || '') + ' · ' + esc(item.lead.via || '') +
                    (item.lead.recurso ? ' · ' + esc(item.lead.recurso) : '') +
                    '</div>';

                if (item.matches.length) {
                    html += renderMatches(item.matches);
                } else {
                    html += '<div style="font-size:13px;color:#aaa;padding:8px 0">Nenhum imóvel compatível</div>';
                }
                html += '</div>';
            }

            html += '</div>';
            document.getElementById('resultMatch').innerHTML = html;
            toast(d.total_leads + ' leads processados');
        } else {
            toast(d.erro, 'erro');
            document.getElementById('resultMatch').innerHTML =
                '<div class="vazio"><div class="emoji">ℹ️</div>' + esc(d.erro) + '</div>';
        }
    } catch(e) {
        document.getElementById('loadMatch').classList.remove('show');
        toast('Erro na conexão', 'erro');
    }
}

// ─── Render Matches ──────────────────────────────────────────────────────────
function renderMatches(matches) {
    return matches.map(m => {
        const nivel = m.score >= 70 ? 'high' : m.score >= 40 ? 'medium' : 'low';
        return '<div class="match-card ' + nivel + '">' +
            '<span class="match-score ' + nivel + '">' + m.score + '%</span>' +
            '<div class="match-title">' + esc(m.titulo) + '</div>' +
            '<div class="match-detail">📍 ' + esc(m.bairro) + ' · 💰 ' + esc(m.valor || '—') +
                ' · 🛏 ' + (m.quartos || '—') + 'Q</div>' +
            (m.motivos ? '<div class="match-motivos">' + m.motivos.map(esc).join(' · ') + '</div>' : '') +
            '<span class="match-tipo">' + esc(m.tipo_match || 'critérios') + '</span>' +
            (m.link ? ' <a href="' + esc(m.link) + '" target="_blank" style="font-size:12px;margin-left:8px">Ver no site →</a>' : '') +
        '</div>';
    }).join('');
}

// ─── Config ──────────────────────────────────────────────────────────────────
function salvarKey() {
    apiKey = document.getElementById('apiKey').value.trim();
    localStorage.setItem('gemini_key', apiKey);
    toast(apiKey ? 'Chave salva' : 'Chave removida — modo critérios');
    carregarImoveis();
}

function atualizarSysStatus() {
    const el = document.getElementById('sysStatus');
    el.innerHTML =
        '<p style="font-size:13px;margin-bottom:6px">🏠 <strong>' + imoveis.length + '</strong> imóveis no site</p>' +
        '<p style="font-size:13px;margin-bottom:6px">🔑 IA Gemini: <strong>' + (apiKey ? 'Ativa' : 'Desligada (match por critérios)') + '</strong></p>' +
        '<p style="font-size:13px">📁 Leads em: G:\\\\Meu Drive\\\\MR-Imoveis\\\\leads</p>';
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function esc(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = String(s);
    return d.innerHTML;
}
</script>
</body>
</html>"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 8080
    print("\n" + "=" * 54)
    print("  MARCOS ROSA — CRM de Leads")
    print("  Match: Critérios + IA (Gemini opcional)")
    print("=" * 54)
    print(f"\n  Acesse:     http://localhost:{PORT}")
    print(f"  Leads em:   {OBSIDIAN_LEADS}")
    print(f"  IA Gemini:  {'Configurar na aba ⚙️' }")
    print(f"\n  Sem chave = match por critérios (funciona sempre)")
    print(f"  Com chave = match refinado por IA")
    print("\n  Ctrl+C para encerrar")
    print("=" * 54 + "\n")

    threading.Timer(1.2, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    app.run(host="0.0.0.0", port=PORT, debug=False)
