# Revisão Completa — imovflow.com.br
**Data:** 2026-03-13
**Profissional:** Marcos Rosa Campos — CRECI-GO 35088-F
**Site:** imovflow.com.br

---

## Contexto

Tema WordPress customizado (`marcos-rosa`) está no ar mas sem divulgação ativa. O objetivo principal do site é duplo: converter visitantes em contatos via WhatsApp e exibir imóveis disponíveis. O plano prioriza estabilidade e impacto de forma incremental, em 3 camadas independentes.

---

## Camada 1 — Crítico (bugs e fluxos quebrados)

### 1.1 Header Duplicado em front-page.php
**Problema:** `front-page.php` chama `get_header()` na linha 1 (carregando o `header.php` correto com id `mr-header`, menu mobile, etc.) mas também contém um bloco `<header>` inline estático nas linhas 4–17 com classes diferentes e sem mobile toggle. Isso resulta em dois headers visíveis na página.
**Solução:** Remover as linhas 4–17 de `front-page.php` (o bloco `<!-- HEADER -->` inline inteiro).
**Aceito quando:** a página tem apenas um header, com logo, navegação funcional e botão WhatsApp.

### 1.2 Footer — Mismatch de Classes CSS
**Problema:** `footer.php` usa classes com prefixo `mr-` mas `main.css` define as versões sem prefixo:
| PHP (footer.php) | CSS (main.css) |
|---|---|
| `.mr-footer-grid` | `.footer-grid` |
| `.mr-footer-brand` | sem equivalente |
| `.mr-footer-desc` | `.footer-desc` |
| `.mr-footer-titulo` | `.footer-col-titulo` |
| `.mr-footer-links` | `.footer-links` |
| `.mr-footer-logo` | `.footer-logo-img` |
| `.mr-footer-creci` | `.footer-creci` |
| `.mr-footer-bottom` | `.footer-bottom` |
| `.mr-footer-copy` | `.footer-copy` |
| `.mr-footer-social` | `.footer-social` |
| `.mr-wpp-float` | `.wpp-float` |

Nota: `.mr-social-btn` já está coberto no CSS (seletor combinado `social-btn, .mr-social-btn`).

**Solução:** Atualizar `footer.php` para usar as classes CSS corretas. Para `.mr-footer-brand` (sem equivalente), usar `footer-brand` e adicionar regra mínima no CSS.
**Aceito quando:** o footer renderiza com layout em grid, tipografia dourada nos títulos, links com hover dourado, linha decorativa visível, e botão WhatsApp flutuante verde no canto inferior direito.

### 1.3 Formulário de Captação — Mismatch HTML/JS
**Problema:** O handler AJAX e a lógica JS já existem e estão corretos em `functions.php` e `main.js`. Existem 4 bugs que impedem o funcionamento:
1. Campos sem atributo `id` (JS busca `cap-nome`, `cap-wpp`, `cap-tipo`, `cap-bairro`, `cap-valor`)
2. Seletor `.mr-btn-captacao` no JS não encontra nada (botão tem classe `btn-captacao`) → `btn` é `null` → `TypeError: Cannot set properties of null` na linha 65 do `main.js` — isso faz a submissão falhar completamente com exceção JS antes do fetch
3. `enviarCaptacao()` nunca é chamada — o botão não tem `onclick` e não há `addEventListener` ligando a função ao botão
4. Sem `<div id="mr-captacao-msg">` para feedback visual

**Solução:**
1. Em `front-page.php`: adicionar `id="cap-nome"`, `id="cap-wpp"`, `id="cap-tipo"`, `id="cap-bairro"`, `id="cap-valor"` nos campos; adicionar `onclick="enviarCaptacao()"` no botão; adicionar `<div id="mr-captacao-msg" style="display:none"></div>` antes do botão
2. Em `main.js`: corrigir `document.querySelector('.mr-btn-captacao')` → `document.querySelector('.btn-captacao')`

**Aceito quando:** submeter o formulário com dados válidos cria um post `captacao` no WP admin, envia email para mrcimoveis78@gmail.com, abre o WhatsApp do proprietário em nova aba, e exibe mensagem de confirmação verde.

### 1.4 Seção Sobre — Foto Ausente
**Problema:** A `.sobre-section` tem `grid-template-columns: 1fr 1fr` no CSS mas `front-page.php` só tem `div.sobre-conteudo` — a coluna da foto está ausente no HTML. O CSS já define `.sobre-foto` e `.sobre-foto img`, e o arquivo `assets/img/marcos-rosa.jpg` já existe.
**Solução:** Adicionar em `front-page.php` antes de `.sobre-conteudo`:
```html
<div class="sobre-foto">
  <img src="<?php echo get_template_directory_uri(); ?>/assets/img/marcos-rosa.jpg" alt="Marcos Rosa — Corretor de Imóveis">
</div>
```
**Aceito quando:** a seção Sobre exibe a foto P&B do Marcos Rosa na coluna esquerda e o texto na coluna direita.

### 1.5 Formulário de Busca — IDs Ausentes e Redirecionamento 404
**Problema:** Os campos de busca não têm `id`, o botão não tem `onclick`, e o redirecionamento aponta para `/imoveis/` que retorna 404 até o CPT imovel existir.
**Solução (curto prazo):** Ocultar a seção `.busca-section` com `display:none` no CSS até o CPT imóveis (item 2.2) estar implementado. Os IDs e o onclick serão adicionados junto com o CPT.
**Aceito quando:** a seção de busca não exibe conteúdo incompleto ao usuário.

### 1.6 Links Sociais no Footer
**Problema:** `footer.php` aponta para `instagram.com`, `facebook.com`, `youtube.com` genéricos.
**Solução:** Confirmar com Marcos Rosa os handles reais antes de editar. Remover os canais sem perfil ativo.
**Aceito quando:** todos os links levam a perfis reais ou foram removidos.

---

## Camada 2 — Alto Impacto

### 2.1 SEO — og:image Ausente
**Status:** Title tag, meta description, Open Graph (exceto imagem) e Twitter Card já implementados em `functions.php`.
**Pendente:** Adicionar `<meta property="og:image">` apontando para a logo dourada do tema.
**Aceito quando:** compartilhar imovflow.com.br no WhatsApp exibe a logo como thumbnail.

### 2.2 CPT Imóveis
- Registrar post type `imovel` em `functions.php` seguindo o padrão do `captacao` já existente
- Campos via `register_post_meta()` + meta box nativa: tipo, bairro, preço, quartos, banheiros, vagas, badge
- Foto do imóvel via `post-thumbnails` (já habilitado)
- Converter os 3 cards estáticos em `WP_Query` dinâmico
- Ativar o formulário de busca (item 1.5) junto com este item
- Cadastrar os primeiros imóveis reais
**Aceito quando:** adicionar/editar posts `imovel` no WP admin reflete nos cards da home.

### 2.3 Responsividade Mobile
- Breakpoints existentes (1024px, 768px) já cobrem header e menu — não duplicar
- Adicionar overrides para: `.hero` (grid 1fr 1fr → coluna única), `.imoveis-grid` (3 colunas → 1), formulário captação, seção CTA
**Aceito quando:** site sem overflow horizontal em 375px (iPhone SE).

---

## Camada 3 — Crescimento

### 3.1 Automação WhatsApp — Server-Side
**Status parcial:** ao enviar o formulário, o JS já abre o WhatsApp do proprietário via `window.open(wpp_link)`.
**Pendente:** Notificação server-side para Marcos Rosa (CallMeBot ou Z-API) como backup ao email.

### 3.2 Google Meu Negócio
- Criar perfil com endereço Anápolis/GO, telefone e link para imovflow.com.br

### 3.3 Instagram
- Confirmar handle real e atualizar bio com link para imovflow.com.br

---

## Ordem de Execução

| Prioridade | Item | Impacto | Esforço |
|---|---|---|---|
| 1 | 1.1 Header duplicado | Crítico visual | Muito baixo |
| 2 | 1.2 Footer CSS mismatch | Crítico visual | Baixo |
| 3 | 1.4 Seção Sobre — foto | Visual imediato | Muito baixo |
| 4 | 1.3 Formulário — IDs | Crítico funcional | Baixo |
| 5 | 1.5 Busca — ocultar | Funcional | Muito baixo |
| 6 | 1.6 Links sociais | Correção (depende de cliente) | Muito baixo |
| 7 | 2.1 SEO og:image | Alto (compartilhamento) | Muito baixo |
| 8 | 2.2 CPT imóveis | Alto (conteúdo real) | Médio |
| 9 | 2.3 Mobile audit | Alto (maioria mobile) | Baixo |
| 10 | 3.1 WA server-side | Médio | Médio |
| 11 | 3.2 Google Meu Negócio | Médio | Muito baixo |
| 12 | 3.3 Instagram bio | Baixo | Muito baixo |

---

## Paleta e Tipografia (referência)

```
--azul:          #1a2744
--azul-medio:    #243457
--dourado:       #c9a84c
--dourado-claro: #e2c97e
--dourado-escuro:#a07c30
--branco:        #f8f6f1
--cinza-claro:   #edeae3

Títulos: Cormorant Garamond (serif)
Corpo:   Josefin Sans (sans-serif)
```
