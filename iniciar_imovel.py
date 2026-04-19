#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iniciar_imovel.py v2.1 - Marcos Rosa Negocios Imobiliarios
Cria estrutura de pastas para um novo imovel em _em-captacao\\<slug>\\

Uso:
    python iniciar_imovel.py <slug>

Exemplo:
    python iniciar_imovel.py casa-flor-cerrado-370mil
"""

import sys
from pathlib import Path

# ============================================================
# FIX ENCODING WINDOWS (resolve UnicodeEncodeError cp1252)
# ============================================================
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
# CONFIGURACAO
# ============================================================
BASE_DRIVE = Path(r"G:\Meu Drive\MR-Imoveis\imoveis\_em-captacao")

# ============================================================
# HELPERS (ASCII puro - nao quebra no Windows)
# ============================================================
def info(msg): print(f"  [INFO] {msg}")
def ok(msg):   print(f"  [OK]   {msg}")
def warn(msg): print(f"  [!]    {msg}")
def err(msg):  print(f"  [ERRO] {msg}"); sys.exit(1)

# ============================================================
# VALIDACAO DE SLUG
# ============================================================
def validar_slug(slug):
    if not slug:
        err("Slug vazio")
    if len(slug) > 40:
        err(f"Slug muito longo ({len(slug)} chars, max 40)")
    if " " in slug:
        err("Slug nao pode ter espacos")
    if slug != slug.lower():
        err(f"Slug deve ser minusculo: '{slug}'")
    for c in slug:
        if not (c.isalnum() or c == '-'):
            err(f"Caractere invalido em slug: '{c}'")

# ============================================================
# MAIN
# ============================================================
def main():
    if len(sys.argv) != 2:
        print("Uso: python iniciar_imovel.py <slug>")
        print("Ex:  python iniciar_imovel.py casa-flor-cerrado-370mil")
        sys.exit(1)

    slug = sys.argv[1].strip()
    validar_slug(slug)

    print("=" * 60)
    print(f"  INICIAR IMOVEL: {slug}")
    print("=" * 60)

    pasta_imovel    = BASE_DRIVE / slug
    pasta_originais = pasta_imovel / "fotos-originais"

    if pasta_imovel.exists():
        warn(f"Pasta ja existe: {pasta_imovel}")
        warn("Continuando (so garante que subpastas existam)...")

    pasta_originais.mkdir(parents=True, exist_ok=True)
    ok(f"Pasta criada: {pasta_imovel}")
    ok(f"Subpasta:     fotos-originais\\")

    print()
    print("-" * 60)
    print("  Proximos passos:")
    print(f"  1. Jogar fotos em: {pasta_originais}")
    print(f"  2. Salvar JSON em: {pasta_imovel}\\imovel-{slug}.json")
    print(f"  3. Rodar:          python publicar.py {slug}")
    print("-" * 60)


if __name__ == "__main__":
    main()
