---
name: marcos-rosa-negocios-imobiliarios
description: Guia operacional completo do pipeline de publicação imobiliária — Marcos Rosa CRECI-GO 35088-F
---

# SKILL.md — Marcos Rosa · Negócios Imobiliários
> Pipeline V2.1 | Atualizado: 20/04/2026

---

## 1. IDENTIDADE

- Profissional: Marcos Rosa Campos | CRECI-GO 35088-F | Anápolis/GO
- Marca: **Marcos Rosa — Negócios Imobiliários** (nunca "IMOVFLOW" em código novo)
- Site: https://imovflow.com.br | WhatsApp: (62) 98114-8448
- Cores: Azul `#1a2744` · Dourado `#c9a84c` · Fontes: Cormorant Garamond / Josefin Sans
- Objetivo estratégico: gerar comissões via rede de parceiros → abrir imobiliária própria
- Tempo disponível: ~2h/dia (manhãs)
- Canal primário: WhatsApp (não email)
- Somente vendas (aluguéis excluídos)

---

## 2. CREDENCIAIS

| Serviço | Credencial |
|---------|-----------|
| SSH KingHost | `imovflow@191.6.209.223` |
| WordPress admin | `marcos_admin` |
| WP App Password | `JdGD SV7X zRSO Gxg1 Vd3T f6FO` |
| WP root | `~/www` · Tema: `~/www/wp-content/themes/marcos-rosa/` |
| GSC service account | `gsc-mcp@imovflow-mcp.iam.gserviceaccount.com` |
| GSC key local | `C:\Users\socra\marcos-rosa-tema\gsc-key.json` |
| GitHub repo | `socramasor12-sudo/imovflow-site` (privado, PAT clássico) |
| Gmail | `socramasor12@gmail.com` |
| Ngrok domain | `intervascular-subdivinely-harper.ngrok-free.dev` |

---

## 3. REGRAS CRÍTICAS (nunca ignorar)

1. **SSH Windows**: sempre `;` — NUNCA `&&` (derruba sessão KingHost)
2. **SCP**: sempre `-o StrictHostKeyChecking=no`
3. **KingHost bloqueia Python**: usar `'User-Agent': 'curl/8.0'` em TODOS os requests HTTP
4. **Windows Python**: prefixar com `PYTHONIOENCODING=utf-8`
5. **Elementor** injeta `img { max-width:100% !important }` globalmente — para lightboxes/modais usar `<div>` + `background-image` + `background-size:contain` em vez de `<img>`. JS seta `backgroundImage` não `src`
6. **Heredoc não confiável**: criar arquivos via base64 + python3 ou SCP
7. **REST API não salva meta fields**: SEMPRE rodar script PHP fix após publicar (`publicar.py` já faz isso automaticamente)
8. **PHP com `wp_generate_attachment_metadata()`**: incluir manualmente `image.php`, `file.php`, `media.php`
9. **PHP scripts**: auto-deletar via `unlink(__FILE__)` + parâmetro `?token=`
10. **Assets**: versionar com `ver=X.X.X` para cache bust
11. **SCP stale**: se enviar resultado antigo, escrever via `python3 -c` com base64 over SSH
12. **SSH post-quantum warning**: inofensivo, ignorar
13. **Favicon**: usar `site_icon` do WP Customizer (attachment ID 331) — não função manual
14. **Plugins perigosos**: W3 Total Cache (conflito LiteSpeed) e EWWW Image Optimizer (recompressão perde watermark) — DESATIVADOS permanentemente
15. **Descrições de imóveis**: Claude pode sugerir um rascunho da descrição a partir dos bullet points/texto bruto que Marcos fornecer. O rascunho é **sugestão** — Marcos revisa, ajusta e aprova antes de salvar no JSON. Nunca inventar características que não estejam no material enviado; se faltar algum dado relevante (área, banheiros, vagas, diferenciais), perguntar antes de escrever. Saída em HTML com `<p>` e, quando couber, `<ul><li>` para diferenciais.
16. **Gemini API automática para descrições**: segue DESCONTINUADA (integração no `publicar.py` removida). Gemini só é usado para matching de leads no CRM. Sugestões de descrição vêm do Claude no chat, com revisão humana obrigatória.
17. **WP-CLI indisponível**: PHP CLI = 5.x — usar scripts PHP fix via curl
18. **Cache clearing**: `rm -rf ~/www/wp-content/cache/* ; rm -rf ~/www/wp-content/litespeed/*`
19. **Taxonomia `tipo_negocio`**: fonte de verdade para classificação lançamento/revenda. Slugs canônicos: `lancamentos` e `revendas` (plural). `publicar.py` atribui via REST API chamada adicional após criar o post. URLs públicas: `/lancamentos-em-anapolis/` e `/revendas-em-anapolis/` (páginas dedicadas com templates customizados). Archive `/imoveis/` usa filtro `?tipo_negocio=`.
20. **`page.php`** deve existir no tema — sem ele, páginas do tipo `page` renderizam em branco (fallback para `index.php` que é `// Silence is golden`). Criado em 02/05/2026.
21. **Nunca deletar `uploads/elementor/css/*`** — pode quebrar páginas que dependem de CSS gerado pelo Elementor.

---

## 4. PIPELINE V2 — PUBLICAÇÃO

### 4.1 Fluxo (2 comandos, ~10 min por imóvel)

```
PASSO 1:  python iniciar_imovel.py <slug>
          → Cria pasta + subpastas em _em-captacao\
          → Abre formulário (fechar se não for usar)

PASSO 2:  Jogar fotos em fotos-originais\

PASSO 3:  Gerar JSON V5 (2 opções):
          • PC: mandar texto pro Claude → Claude gera JSON V5
          • Celular/parceiro: preencher formulário HTML → JSON V4

PASSO 4:  python publicar.py <slug>
          → Valida → Resumo → Confirmação → Otimiza fotos
          → Upload REST API → Cria post → PHP fix → Cache
          → Obsidian → Move para _publicados → Abre URL
```

### 4.2 Scripts

| Script | Local | Função |
|--------|-------|--------|
| `iniciar_imovel.py` | `C:\Users\socra\marcos-rosa-tema\` | Cria estrutura de pastas + abre formulário |
| `publicar.py` | `C:\Users\socra\marcos-rosa-tema\` | **V2 unificado**: otimiza + publica + PHP fix + cache + Obsidian + move pasta |
| `marcos_rosa_otimizador.py` | `C:\Users\socra\marcos-rosa-tema\` | Chamado internamente pelo publicar.py |
| `mr_crm.py` | `C:\Users\socra\marcos-rosa-tema\` | CRM Flask (porta 8080) |

### 4.3 Regra do slug

Formato: `<tipo>-<bairro-curto>-<valor>` — máx. 40 chars, sem acentos, sem espaços.
Exemplos: `casa-flor-cerrado-370mil` · `apto-jundiai-280mil` · `terreno-jd-paris-120mil`

### 4.4 JSON V5 (formato flat — gerado pelo Claude)

```json
{
  "titulo": "Casa 3 Quartos Suíte — Flor do Cerrado, Anápolis",
  "slug": "casa-flor-cerrado-370mil",
  "tipo": "casa",
  "finalidade": "venda",
  "tipo_negocio": "revendas",
  "valor": 370000,
  "area": 105,
  "quartos": 3,
  "banheiros": 2,
  "vagas": 2,
  "bairro": "Flor do Cerrado",
  "cidade": "Anápolis",
  "estado": "GO",
  "descricao": "<p>Texto HTML da descrição.</p>",
  "seo_title": "Casa 3 Quartos Suíte Flor do Cerrado Anápolis R$ 370 mil",
  "seo_description": "Meta description até 155 caracteres.",
  "foto_capa": "",
  "parceiro": { "nome": "", "creci": "", "whatsapp": "" }
}
```

Template em: `C:\Users\socra\marcos-rosa-tema\template-v5.json`
O `publicar.py` aceita tanto V5 (flat) quanto V4 (nested, do formulário).

### 4.5 O que o publicar.py V2 faz automaticamente

- Busca qualquer `imovel-*.json` na pasta (sem exigir nome exato)
- Valida campos obrigatórios antes de publicar
- Detecta se título parece slug (erro comum)
- Verifica duplicata no WordPress (evita posts `-2`)
- Mostra resumo visual e pede confirmação
- Otimiza fotos (chama otimizador)
- Upload via REST API com `User-Agent: curl/8.0`
- Cria post CPT `imovel`
- Gera e executa PHP fix (meta fields + post_parent + thumbnails)
- Limpa cache LiteSpeed via SSH
- Cria nota `.md` no Obsidian com ID, URL, dados
- Move pasta de `_em-captacao` para `_publicados`
- Abre URL no navegador

### 4.6 Deploy padrão (para scripts PHP avulsos)

```
1. Escrever arquivo local  → Out-File -Encoding utf8
2. SCP                     → scp -o StrictHostKeyChecking=no arquivo.php imovflow@191.6.209.223:~/www/
3. Executar                → curl -s "https://imovflow.com.br/arquivo.php?token=TOKEN"
4. Verificar auto-delete   → ssh imovflow@191.6.209.223 "ls -la ~/www/arquivo.php"
5. Limpar cache            → rm -rf ~/www/wp-content/cache/* ; rm -rf ~/www/wp-content/litespeed/*
```

Alternativa (SCP falhar): `ssh imovflow@191.6.209.223 "python3 -c \"import base64; open('~/www/arquivo.php','wb').write(base64.b64decode('BASE64'))\""`

---

## 5. WORDPRESS

- CPT: `imovel` — REST endpoint: `/wp-json/wp/v2/imovel/{id}`
- mu-plugin: `mr-rest-meta.php` — expõe meta fields customizados na REST API
- Meta fields obrigatórios: `_imovel_tipo`, `_imovel_finalidade`, `_imovel_valor`, `_imovel_area`, `_imovel_quartos`, `_imovel_banheiros`, `_imovel_vagas`, `_imovel_bairro`, `_imovel_galeria`
- Futuros (parceiros): `_corretor_nome`, `_corretor_creci`, `_corretor_whatsapp`
- Lightbox em `single-imovel.php`: usa `<div>` + `background-image` (não `<img>`)
- Plugins ativos: Akismet, Contact Form 7, JoinChat, Elementor, Insert Headers/Footers, Limit Login Attempts, LiteSpeed Cache, Regenerate Thumbnails, Yoast SEO
- Plugins desativados: W3 Total Cache, EWWW Image Optimizer
- Taxonomia `tipo_negocio` (`lancamentos` | `revendas`) — registrada em `functions.php`, exposta via REST API

### Posts publicados (11 imóveis)

| Slug | Imóvel | Tipo Negócio |
|------|--------|--------------|
| `apto-arpoador-jundiai-711mil` | Apto Arpoador Jundiaí | lancamentos |
| `lote-ecoville-colorado-360-450m2` | Lotes Ecoville Colorado | lancamentos |
| `casa-3-quartos-suite-summerville-anapolis-go` | Casa Summerville | revendas |
| `casa-4-quartos-com-1-suite-no-frei-eustaquio-anapolis-go` | Casa Frei Eustáquio | revendas |
| `casa-setor-sul-580mil` | Casa Setor Sul 3ª Etapa | revendas |
| `casa-flor-do-cerrado-370mil` | Casa Flor do Cerrado | revendas |
| `casa-vivian-parque-360mil` | Casa Vivian Parque | revendas |
| `casa-escala-norte-350mil` | Casa Escala Norte | revendas |
| `lote-roses-garden-270mil` | Lote Roses Garden | revendas |
| `casa-vila-formosa-360mil` | Casa Vila Formosa | revendas |
| `casa-via-lagos-nova-crixas-550mil` | Casa Via dos Lagos | revendas |

## SEO

- Schema.org `RealEstateListing` em `single-imovel.php` (auto-gerado a partir de meta fields)
- `BreadcrumbList` JSON-LD em `single-imovel.php`
- Sitemap Yoast: `/sitemap_index.xml` (validar inclusão de CPT `imovel` e taxonomia `tipo_negocio`)
- Title default home: "Corretor de Imóveis em Anápolis/GO | Marcos Rosa — CRECI-GO 35088-F"

---

## 6. CRM (`mr_crm.py`)

- Flask, porta 8080 — `C:\Users\socra\marcos-rosa-tema\mr_crm.py`
- Interface mobile-first, entrada de lead em linguagem natural
- Campo `recurso`: financiamento / aprovado / próprio / permuta
- Matching 2 camadas: critérios fixos (sempre funciona) + Gemini 2.5 Flash Lite (opcional, aba ⚙️)
- Batch matching: botão "Match todos os novos" — lê pasta `leads/` do Obsidian
- Acesso celular/4G: ngrok → `https://intervascular-subdivinely-harper.ngrok-free.dev`
- Startup: `C:\Users\socra\iniciar-crm.bat` (atalho Área de Trabalho) — abre CRM + ngrok

---

## 7. OBSIDIAN

- Vault: `G:\Meu Drive\MR-Imoveis\`
- Sync: Google Drive ↔ FolderSync desativado (só Google Drive app no celular para enviar fotos)
- Kanban de leads: `kanban-leads` → Novo / Contactar / Negociando / Fechado / Perdido
- Dashboard Dataview: ativo
- Template de lead: `nome/tel/via/recurso/status/prox`
- QuickAdd: `Ctrl+Shift+L`
- Plugins: Dataview, Kanban, Tasks, Templater, QuickAdd

---

## 8. FORMULÁRIOS

| Formulário | Uso | Quando |
|------------|-----|--------|
| `formulario_marcos.html` | Interno (Marcos) | Celular / quando não tiver Claude |
| `formulario_corretor.html` | Corretores parceiros | Envio via WhatsApp |
| Texto direto → Claude → JSON V5 | PC (mais rápido) | Modo principal de publicação |

Formulários ficam em: `G:\Meu Drive\MR-Imoveis\formularios\`

---

## 9. ESTRUTURA DE PASTAS

```
G:\Meu Drive\MR-Imoveis\
├── imoveis\
│   ├── _em-captacao\          ← imóveis em preparo
│   │   └── <slug>\
│   │       ├── fotos-originais\
│   │       ├── fotos-prontas\    (gerado pelo otimizador)
│   │       └── imovel-<slug>.json
│   └── _publicados\           ← imóveis já no site
│       └── <slug>\
│           ├── fotos-originais\
│           ├── fotos-prontas\
│           ├── imovel-<slug>.json
│           └── <slug>.md       (nota Obsidian)
├── leads\                     ← notas de leads (Kanban)
├── formularios\               ← HTMLs dos formulários
└── kanban-leads.md

C:\Users\socra\marcos-rosa-tema\
├── publicar.py                ← pipeline V2 unificado
├── iniciar_imovel.py          ← cria estrutura de pastas
├── marcos_rosa_otimizador.py  ← otimização de fotos
├── mr_crm.py                  ← CRM Flask
├── iniciar-crm.bat            ← atalho CRM + ngrok
├── template-v5.json           ← template JSON flat
├── GUIA-RAPIDO.md             ← guia para Marcos
└── assets\watermark.png       ← watermark
```

---

## 10. MODELO DE PARCERIAS (planejado, não implementado)

### Conceito
Corretores parceiros enviam imóveis → Marcos publica → Leads chegam → CRM faz match → Marcos qualifica → Repassa ao parceiro. Visitante do site não sabe que parceiros existem.

### Fases (quando tiver volume)

| Fase | O que | Status |
|------|-------|--------|
| A | Pipeline unificado (`publicar.py`) | ✅ Concluído |
| B | Meta fields parceiro + esquema MR-XXX | Pendente |
| C | Página `/parceiros/` (oculta, link direto) | Pendente |
| D | CRM mostra dono do imóvel no match | Pendente |
| E | Checagem de duplicatas entre parceiros | Pendente |
| F | Notificação WhatsApp automática | Pendente |

### Regras de negócio (Marcos define)
- [ ] Split de comissão
- [ ] Exclusividade de anúncio
- [ ] Marcos intermedia ou repassa direto
- [ ] Limite de imóveis por parceiro
- [ ] Prazo de retorno sobre lead quente

---

## 11. PENDÊNCIAS PRIORITÁRIAS

### Agora (gera comissão)
- Subir mais imóveis (meta: 10+)
- Fazer primeira parceria real
- Testar `publicar.py` V2 com imóvel real

### Quando tiver volume (10+ imóveis)
- Meta fields de parceiro (Fase B)
- Página `/parceiros/` (Fase C)
- CRM com dono do imóvel (Fase D)

### Quando escalar (20+ imóveis, parceiros ativos)
- Cloudflare Tunnel (substituir ngrok)
- Checagem de duplicatas (Fase E)
- Notificação WhatsApp (Fase F)

---

## 12. FERRAMENTAS

- **Claude Code** (extensão VS Code): operações SSH/SCP/Git
- **MCPs ativos**: Gmail, Google Calendar, Google Search Console, GitHub, Canva, Google Drive
- **Bibliotecas Python**: Pillow, pillow-heif, requests, Flask, paramiko
- **GSC MCP**: `@adenot/mcp-google-search-console` · config: `C:\Users\socra\.claude.json`

---

## 13. PADRÃO DE RESPOSTA DA IA

- Fluxo: Objetivo → Código → Deploy → Validação
- Sem plugins desnecessários
- Sem `&&` em SSH
- Sem declarar sucesso sem validar com `curl`/`ls`
- Nunca modificar banco de dados sem backup
- Descrições de imóveis: Claude sugere rascunho → Marcos revisa e aprova → JSON final
- Ao gerar rascunho, Claude NUNCA inventa características; se faltar dado relevante, pergunta antes
- Explicações em linguagem clara
- Respostas diretas e práticas (tempo limitado)
- Para gerar JSON V5: Marcos manda texto livre → IA gera JSON flat → salva na pasta do imóvel

---

## SPRINT 1 — ROBUSTEZ DO PIPELINE (20/04/2026)

Sprint 1 concluido. 3 melhorias estruturais:

**1. Validacao Pydantic (`schema_imovel.py`)**
- Novo arquivo: `C:\Users\socra\marcos-rosa-tema\schema_imovel.py`
- Define modelo `Imovel` com tipos, ranges e enums
- Converte V4 (nested, do formulario) para V5 (flat) via `normalizar_v4_para_v5()`
- Mapa V4 real documentado:
  - `informacoes_basicas.titulo` -> titulo
  - `classificacao.tipo_principal` -> tipo
  - `caracteristicas.area_total` ou `area_construida` -> area
  - `descricao.breve` + `diferenciais` + `observacoes` -> descricao (HTML)
  - `seo.titulo_seo` -> seo_title
- Publicar fail fast: se invalido, imprime erros e aborta antes de upload

**2. Guardrail em `iniciar_imovel.py`**
- Checa 3 fontes antes de criar pasta:
  1. `_publicados/<slug>/` existe? -> aborta
  2. `_em-captacao/<slug>/` existe com JSON ou fotos? -> aborta
  3. WordPress REST API ja tem o slug? -> aborta
- Pasta vazia em `_em-captacao/` permite retomada (warn, nao err)
- WP offline: warn, prossegue (nao acopla dependencia externa)

**3. Logging persistente em `publicar.py`**
- Cada execucao: `logs/publicar-<slug>-<timestamp>.log`
- Suporta `--dry-run` (sufixo `-dryrun` no nome)
- Tee duplica stdout/stderr (tela + arquivo)
- `errors="replace"` no open (defesa encoding Windows)
- `atexit` garante fechamento do file handle

**Comportamentos estabelecidos (auditoria do dia):**

- `_publicados/` = registro imutavel. Nunca editar JSONs la retroativamente.
- Slug do argumento tem precedencia sobre slug do JSON. Divergencia = warn `[!]`.
- JSONs V4 ja publicados sao imutaveis (regra C - nao reprocessar).

**Dividas reconhecidas (pendentes):**

- Sprint 2: atomicidade do `publicar.py` (sem rollback/manifest em caso de falha)
- Fonte de verdade do slug e a pasta, nao o JSON (consciente, valido enquanto so Marcos opera)
- Inventario V4 -> V5 incompleto (campos ignorados: `condicoes_pagamento`, `proprietario.*`, `captacao.corretor`, `suites`, `andar`, `observacoes`, `endereco`). Revisitar quando parceiros entrarem.
- Credenciais WP em plaintext no `publicar.py` - migrar para .env antes de parceiros

**Arquivos novos/modificados hoje:**

- NOVO: `schema_imovel.py` (170 linhas, Pydantic + normalizador V4->V5)
- MOD: `publicar.py` (carregar_json unificado, validar_dados via Pydantic, slug warn, logging unificado)
- MOD: `iniciar_imovel.py` (guardrail 3 fontes)
- MOD: `publicar.py` (watermark centralizado 25% / opacidade 55%)
- Backups `.bak-20260419-*` preservados em `C:\Users\socra\marcos-rosa-tema\`

---

## PROBLEMAS RESOLVIDOS — ADICIONADOS 20/04/2026

### P-10: Foto de perfil cortando topo da cabeca
- **Causa**: `.sobre-foto img` com `object-fit: cover` + container 600px alto cortava
  o topo da cabeca porque a foto original eh retrato alto
- **Solucao**: trocar para `object-fit: contain` APENAS nas 2 regras da
  `.sobre-foto` (linhas 220 e 231 do main.css). Cards de imoveis
  (`.imovel-img img`, linhas 177 e 646) DEVEM continuar com `cover`
- **NUNCA** fazer `sed global` de `cover` -> `contain` — quebra os cards
- **Arquivos criticos**: `marcos-rosa-desktop.jpg` e `marcos-rosa-retina.jpg`
  em `~/www/wp-content/themes/marcos-rosa/assets/img/`. Se sumirem, o
  `front-page.php:84-85` referencia esses nomes exatos

### P-11: Arquivos de imagem do tema sumindo sem explicacao
- **Ocorrencia**: 20/04/2026, `marcos-rosa-desktop.jpg` e `-retina.jpg`
  ausentes do servidor. Backups locais em `C:\Users\socra\Downloads\`
  resolveram (datados de 03/04)
- **Pendencia**: configurar backup automatico do `~/www/wp-content/themes/marcos-rosa/assets/img/`
  (Sprint 3, antes de aceitar parceiros)
