# Camada 2 — Design Spec
**Data:** 2026-03-14
**Site:** imovflow.com.br — Marcos Rosa Corretor
**Abordagem:** A — tudo em `functions.php`, sem arquivos extras

---

## 2.1 SEO — og:image

**Arquivo:** `functions.php` → função `marcos_rosa_seo_meta()`

Adicionar uma linha:
```php
<meta property="og:image" content="<?php echo esc_url(get_template_directory_uri()); ?>/assets/img/logo.png">
<meta property="og:image:width" content="200">
<meta property="og:image:height" content="200">
```

**Aceito quando:** compartilhar imovflow.com.br no WhatsApp exibe a logo como thumbnail.

---

## 2.2 CPT Imóveis

### Registro do post type

Em `functions.php`, nova função `marcos_rosa_cpt_imovel()` com `add_action('init', ...)`:

```
post_type: 'imovel'
label: 'Imóveis'
public: true
show_in_menu: true
menu_icon: dashicons-admin-home
rewrite: ['slug' => 'imoveis']
supports: ['title', 'thumbnail']
```

### Meta box + campos

Função `marcos_rosa_imovel_meta_box()` + `marcos_rosa_save_imovel_meta()`:

| Campo | `meta_key` | Tipo | Placeholder |
|---|---|---|---|
| Tipo | `_imovel_tipo` | select | Apartamento / Casa / Terreno / Comercial |
| Bairro | `_imovel_bairro` | text | ex: Jundiaí |
| Preço | `_imovel_preco` | text | ex: 350.000 |
| Quartos | `_imovel_quartos` | number | — |
| Banheiros | `_imovel_banheiros` | number | — |
| Vagas | `_imovel_vagas` | number | — |
| Badge | `_imovel_badge` | text | ex: LANÇAMENTO |

Nonce: `marcos_rosa_imovel_nonce` / `marcos_rosa_save_imovel`.

### WP_Query nos cards

Em `front-page.php`, substituir os 3 `<div class="imovel-card">` estáticos por loop dinâmico:

```php
$imoveis = new WP_Query(['post_type' => 'imovel', 'posts_per_page' => 3, 'post_status' => 'publish']);
while ($imoveis->have_posts()) { $imoveis->the_post(); ... }
wp_reset_postdata();
```

Quando não há imóveis: seção `.imoveis` oculta via `if (!$imoveis->have_posts()) return;` antes do HTML.

### Busca

Manter `.busca-section` oculta no CSS (`display: none`) até haver imóveis cadastrados — ativação será feita em sessão separada com os primeiros dados reais.

**Aceito quando:** criar post `imovel` no WP admin → aparece no card da home.

---

## 2.3 Responsividade Mobile

Breakpoint alvo: 375px (iPhone SE). Breakpoints existentes: 1024px (tablet), 768px (mobile header).

### Overrides a adicionar no CSS (dentro de `@media (max-width: 768px)`)

| Seletor | Problema | Fix |
|---|---|---|
| `.hero` | grid 2 colunas → overflow | `grid-template-columns: 1fr; min-height: auto` |
| `.hero-esquerda` | padding excessivo | `padding: 100px 24px 60px` |
| `.hero-direita` | altura fixa → corte | `height: 300px` |
| `.hero-stats` | `position: absolute` → sai da tela | `position: static; padding: 32px 24px; background: var(--azul-medio); flex-wrap: wrap; gap: 24px` |
| `.imoveis-grid` | 3 colunas → minúsculas | `grid-template-columns: 1fr` |
| `.busca-section` | padding excessivo | `padding: 40px 24px` |
| `.sobre-section` | grid 2 col → estreito | `grid-template-columns: 1fr; padding: 60px 24px` |
| `.sobre-foto` | altura fixa → corte | `min-height: 300px` |
| `.captacao-section` | grid 2 col | `grid-template-columns: 1fr; padding: 60px 24px` |
| `.cta-section` | padding excessivo | `padding: 60px 24px` |
| `.footer` / `.mr-footer` | grid 4 col | `grid-template-columns: 1fr; gap: 40px; padding: 60px 24px 40px` |
| `.mr-footer-grid` | grid 4 col | `grid-template-columns: 1fr` |
| `.wpp-float`, `.mr-wpp-float` | tamanho confortável | `width: 48px; height: 48px; bottom: 20px; right: 16px` |

**Aceito quando:** sem overflow horizontal em 375px.

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `functions.php` | og:image + CPT imovel + meta box + save handler |
| `front-page.php` | WP_Query nos cards de imóveis |
| `assets/css/main.css` | overrides mobile 768px |
