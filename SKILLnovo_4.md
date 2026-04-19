---
name: marcos-rosa-tema
description: Guia operacional completo do pipeline de publicação imobiliária — Marcos Rosa CRECI-GO 35088-F
---

# SKILL.md — Marcos Rosa · Negócios Imobiliários
> Fase 5 concluída | Atualizado: 29/03/2026 (lightbox + favicon + cards mobile corrigidos)

---

## IDENTIDADE
- Profissional: Marcos Rosa Campos | CRECI-GO 35088-F | Anápolis/GO
- Marca: **Marcos Rosa — Negócios Imobiliários** (nunca "IMOVFLOW" em código novo)
- Site: https://imovflow.com.br | WhatsApp: (62) 98114-8448
- Cores: Azul `#1a2744` · Dourado `#c9a84c` · Fontes: Cormorant Garamond / Josefin Sans

---

## SERVIDOR
- KingHost · SSH: `imovflow@191.6.209.223` · WordPress: `~/www`
- Tema: `~/www/wp-content/themes/marcos-rosa/`
- **WP-CLI indisponível** (PHP CLI = 5.x)
- Cache: `find ~/www/wp-content/cache -type f -delete ; find ~/www/wp-content/litespeed -type f -delete`
- Validação: `curl -s -o /dev/null -w '%{http_code}' https://imovflow.com.br` → esperado 200

---

## CREDENCIAIS
- SSH user: `imovflow` | IP: `191.6.209.223`
- WordPress admin: `marcos_admin`
- App Password WP: `JdGD SV7X zRSO Gxg1 Vd3T f6FO`
- GSC service account: `gsc-mcp@imovflow-mcp.iam.gserviceaccount.com`
- GSC key local: `C:\Users\socra\marcos-rosa-tema\gsc-key.json`
- GitHub repo: `socramasor12-sudo/imovflow-site` (PAT clássico na URL do remote)

---

## REGRAS CRÍTICAS (nunca ignorar)
1. **SSH Windows**: sempre `;` — NUNCA `&&` (derruba sessão)
2. **SCP**: sempre `-o StrictHostKeyChecking=no`
3. **KingHost bloqueia Python**: usar `'User-Agent': 'curl/8.0'` em todos os requests
4. **Windows Python**: prefixar com `PYTHONIOENCODING=utf-8`
5. **Elementor** injeta `img { max-width:100% !important }` globalmente — sobrescreve até inline styles e `setProperty('...','important')` em tags `<img>`. Para lightboxes/modais, usar `<div>` com `background-image` + `background-size:contain` em vez de `<img>`. JS deve setar `backgroundImage` em vez de `src`
6. **Heredoc não confiável**: criar arquivos via base64 + python3 ou SCP
7. **REST API não salva meta fields**: sempre rodar script PHP fix após publicar
8. **PHP com `wp_generate_attachment_metadata()`**: incluir manualmente `image.php`, `file.php`, `media.php` — `wp-load.php` sozinho não carrega
9. **PHP scripts**: auto-deletar via `unlink(__FILE__)` + token de segurança
10. **Assets**: versionar com `ver=X.X.X` para forçar cache bust
11. **SCP stale**: se transferência produzir resultado antigo, escrever diretamente no servidor via `python3 -c` com base64
12. **SSH post-quantum warning**: aviso de troca de chave pós-quântica na conexão é inofensivo, pode ignorar
13. **Favicon**: usar `site_icon` do WP Customizer (não função manual) — remover `marcos_rosa_favicon()` do functions.php. Favicon no Google leva 1-3 semanas para atualizar após mudança
14. **Plugins perigosos**: W3 Total Cache (conflito com LiteSpeed) e EWWW Image Optimizer (recompressão dupla, perde watermark) devem permanecer desativados

---

## DEPLOY — PADRÃO CONFIÁVEL
```
1. Escrever arquivo local  → Out-File -Encoding utf8
2. SCP                     → scp -o StrictHostKeyChecking=no arquivo.php imovflow@191.6.209.223:~/www/
3. Executar                → curl -s "https://imovflow.com.br/arquivo.php?token=SEU_TOKEN"
4. Verificar auto-delete   → ssh imovflow@191.6.209.223 "ls -la ~/www/arquivo.php"
5. Limpar cache            → find ~/www/wp-content/cache -type f -delete ; find ~/www/wp-content/litespeed -type f -delete
```

**Alternativa (quando SCP falhar):** escrever diretamente no servidor:
```bash
ssh imovflow@191.6.209.223 "python3 -c \"import base64; open('~/www/arquivo.php','wb').write(base64.b64decode('BASE64_AQUI'))\""
```

---

## PIPELINE DE PUBLICAÇÃO (Fase 5 — operacional)
```
fotos originais
  → marcos_rosa_otimizador.py   (16:9, blur pillarbox, watermark, EXIF)
  → marcos_rosa_publicar.py     (REST API WordPress)
  → script PHP fix              (meta fields + post_parent attachments)
  → imóvel publicado no site
```

### Otimizador (`marcos_rosa_otimizador.py`)
- Resize para 16:9
- Blur pillarbox para fotos em retrato (portrait)
- Compressão + correção EXIF
- Watermark aplicado
- Suporte a HEIC via `pillow-heif`

### Publicador (`marcos_rosa_publicar.py`)
- Publica via REST API com header `User-Agent: curl/8.0`
- Requer script PHP fix pós-publicação para salvar meta fields

### Batch (`marcos_rosa_lote.py`)
- Lê: `G:\Meu Drive\MR-Imoveis\imoveis.xlsx`
- Fotos: `G:\Meu Drive\MR-Imoveis\prontas\[pasta-imovel]\`
- Filtra duplicatas (arquivos terminando em `-2`)
- Limite: 9 fotos por imóvel
- Converte pipe `|` → lista HTML `<ul><li>`
- SEO title: Marcos prefere escrever manualmente

---

## WORDPRESS
- Admin URL: `imovflow.com.br/wp-admin`
- CPT: `imovel`
- Meta fields obrigatórios:
  - `_imovel_tipo`
  - `_imovel_finalidade`
  - `_imovel_valor`
  - `_imovel_area`
  - `_imovel_quartos`
  - `_imovel_banheiros`
  - `_imovel_vagas`
  - `_imovel_bairro`
- Após publicar: script PHP fix seta todos os meta fields + `post_parent` em todos os attachments
- Plugin necessário: **Regenerate Thumbnails** (já instalado, 49 thumbnails regenerados)
- Favicon: `site_icon` = attachment ID 331 (`logo-site-icon.png`)
- **Plugins ativos**: Akismet, Contact Form 7, JoinChat, Elementor, Insert Headers/Footers, Limit Login Attempts, LiteSpeed Cache, Regenerate Thumbnails, Yoast SEO
- **Plugins desativados**: W3 Total Cache (conflito LiteSpeed), EWWW Image Optimizer (recompressão)
- **Lightbox** do `single-imovel.php`: usa `<div>` + `background-image` (não `<img>`) para evitar override do Elementor

### Posts publicados
| ID  | Imóvel                                       |
|-----|----------------------------------------------|
| 279 | Casa Summerville                             |
| 306 | Casa Frei Eustáquio                          |
| 326 | Apartamento Residencial Espanha, Jundiaí     |

Posts duplicados 260 e 261 — **deletados**.

---

## ARQUIVOS LOCAIS
- Projeto: `C:\Users\socra\marcos-rosa-tema\`
- Descrições: `C:\Users\socra\marcos-rosa-tema\descricoes\`
- Planilha batch: `G:\Meu Drive\MR-Imoveis\imoveis.xlsx`
- Fotos prontas: `G:\Meu Drive\MR-Imoveis\prontas\`
- Templates por tipo: `G:\Meu Drive\MR-Imoveis\prontas\TEMPLATE_*`
- Forms de descrição: `G:\Meu Drive\MR-Imoveis\formularios\`

### Estrutura de descrições (`descricoes\`)
Formato plain-text estruturado:
```
TITULO SEO / CONTEUDO / DESCRICAO / CALL TO ACTION / ASSINATURA / CONTATO
```

---

## FORMULÁRIO DE METADADOS
- Arquivo: `formulario_v4_melhorado.html`
- Gera JSON para listagem de imóveis
- Campo SEO title com contador de caracteres
- Auto-geração de slug
- Botões: Download / Copy / Share
- Otimizado para uso mobile e compartilhamento com corretores parceiros

---

## GOOGLE SEARCH CONSOLE
- Configurado via MCP: `@adenot/mcp-google-search-console`
- Config local: `C:\Users\socra\.claude.json`
- Sitemap submetido
- Monitoramento de indexação em andamento

---

## FERRAMENTAS
- **Claude Code** (extensão VS Code): operações SSH/SCP/Git — preferido para sessões longas
- **Antigravity**: scripts PHP/Python via SSH
- **MCPs instalados**: Context7, GitHub, Playwright, Google Workspace, Figma, Google Search Console
- **Bibliotecas Python**: Pillow, pillow-heif, google-auth, google-api-python-client

---

## PADRÃO DE RESPOSTA DA IA
- Objetivo → Código → Deploy → Validação
- Sem plugins desnecessários
- Sem `&&` em SSH
- Sem declarar sucesso sem validar com curl/ls
- Nunca modificar banco de dados sem backup
- **Descrições de imóveis**: sempre escritas por Marcos a partir de bullets — nunca geradas por IA
- Integração Gemini API: **descontinuada permanentemente**
- Explicações em linguagem clara (Marcos tem background técnico limitado)
