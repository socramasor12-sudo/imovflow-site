# Camada 2 — Design Spec
**Data:** 2026-03-14
**Site:** imovflow.com.br — Marcos Rosa Corretor
**Abordagem:** A — tudo em `functions.php`, sem arquivos extras

---

## 2.1 SEO — og:image + twitter:image

**Arquivo:** `functions.php` → função `marcos_rosa_seo_meta()`

Adicionar dentro do bloco de Open Graph existente:
```php
<meta property="og:image"        content="<?php echo esc_url(get_template_directory_uri()); ?>/assets/img/logo.png">
<meta property="og:image:width"  content="512">
<meta property="og:image:height" content="512">
<meta name="twitter:image"       content="<?php echo esc_url(get_template_directory_uri()); ?>/assets/img/logo.png">
```

Nota: `logo.png` é a imagem disponível. Dimensões declaradas como 512x512 (estimada); substituir por valores reais se a imagem for redimensionada. WhatsApp aceita imagens quadradas ≥ 300px.

**Aceito quando:** compartilhar imovflow.com.br no WhatsApp exibe a logo como thumbnail.

---

## 2.2 CPT Imóveis

### Registro do post type

Nova função `marcos_rosa_cpt_imovel()` com `add_action('init', 'marcos_rosa_cpt_imovel')`:

```php
register_post_type('imovel', [
    'label'               => 'Imóveis',
    'public'              => true,
    'show_ui'             => true,
    'show_in_menu'        => true,
    'menu_icon'           => 'dashicons-admin-home',
    'rewrite'             => ['slug' => 'imoveis', 'with_front' => false],
    'supports'            => ['title', 'thumbnail'],
    'capability_type'     => 'post',
]);
```

### Meta box

Registro via hook `add_meta_boxes`:

```php
add_meta_box(
    'marcos_rosa_imovel_detalhes',   // ID
    'Detalhes do Imóvel',            // título no admin
    'marcos_rosa_imovel_meta_box',   // callback de renderização
    'imovel',                        // screen
    'normal',                        // context
    'high'                           // priority
);
```

Campos renderizados pelo callback `marcos_rosa_imovel_meta_box($post)`:

| Campo | `meta_key` | Tipo input | Opções / placeholder |
|---|---|---|---|
| Tipo | `_imovel_tipo` | `<select>` | Apartamento, Casa, Terreno, Comercial |
| Bairro | `_imovel_bairro` | `<input text>` | ex: Jundiaí |
| Preço | `_imovel_preco` | `<input text>` | ex: 350.000 |
| Quartos | `_imovel_quartos` | `<input number>` | — |
| Banheiros | `_imovel_banheiros` | `<input number>` | — |
| Vagas | `_imovel_vagas` | `<input number>` | — |
| Badge | `_imovel_badge` | `<input text>` | ex: LANÇAMENTO |

Nonce: `wp_nonce_field('marcos_rosa_save_imovel', 'marcos_rosa_imovel_nonce')`.

### Save handler

Função `marcos_rosa_save_imovel_meta($post_id)`, hook `save_post_imovel`:

- Guard/early-exit (neste ordem, cada um com `return $post_id` em caso de falha):
  1. `if ( defined('DOING_AUTOSAVE') && DOING_AUTOSAVE ) return $post_id;`
  2. `if ( ! isset($_POST['marcos_rosa_imovel_nonce']) ) return $post_id;`
  3. `if ( ! wp_verify_nonce($_POST['marcos_rosa_imovel_nonce'], 'marcos_rosa_save_imovel') ) return $post_id;`
  4. `if ( ! current_user_can('edit_post', $post_id) ) return $post_id;`
- Todos os campos: `sanitize_text_field()` — incluindo `_imovel_preco` (armazenar string bruta "350.000", exibir como recebido)
- `_imovel_quartos`, `_imovel_banheiros`, `_imovel_vagas`: `absint()`

### WP_Query nos cards

Em `front-page.php`, substituir o bloco inteiro `<section class="imoveis-section">` por estrutura condicional:

```php
<?php
$imoveis = new WP_Query([
    'post_type'      => 'imovel',
    'posts_per_page' => 3,
    'post_status'    => 'publish',
]);
if ($imoveis->have_posts()) : ?>
<section class="imoveis-section" id="imoveis">
  ... header da seção ...
  <div class="imoveis-grid">
    <?php while ($imoveis->have_posts()) : $imoveis->the_post();
      $tipo      = get_post_meta(get_the_ID(), '_imovel_tipo',      true);
      $bairro    = get_post_meta(get_the_ID(), '_imovel_bairro',    true);
      $preco     = get_post_meta(get_the_ID(), '_imovel_preco',     true);
      $quartos   = get_post_meta(get_the_ID(), '_imovel_quartos',   true);
      $banheiros = get_post_meta(get_the_ID(), '_imovel_banheiros', true);
      $vagas     = get_post_meta(get_the_ID(), '_imovel_vagas',     true);
      $badge     = get_post_meta(get_the_ID(), '_imovel_badge',     true);
    ?>
    <div class="imovel-card">
      <div class="imovel-img">
        <?php if (has_post_thumbnail()) :
          the_post_thumbnail('medium', ['class' => 'imovel-thumb']);
        else : ?>
          <div class="imovel-img-placeholder">MR</div>
        <?php endif; ?>
        <?php if ($badge) : ?>
          <div class="imovel-badge"><?php echo esc_html($badge); ?></div>
        <?php endif; ?>
      </div>
      <div class="imovel-info">
        <div class="imovel-tipo"><?php echo esc_html($tipo); ?></div>
        <div class="imovel-nome"><?php the_title(); ?></div>
        <?php if ($bairro) : ?>
          <div class="imovel-local">📍 <?php echo esc_html($bairro); ?>, Anápolis/GO</div>
        <?php endif; ?>
        <?php if ($preco) : ?>
          <div class="imovel-preco">R$ <?php echo esc_html($preco); ?></div>
        <?php endif; ?>
        <?php if ($quartos || $banheiros || $vagas) : ?>
        <div class="imovel-detalhes">
          <?php if ($quartos)   echo '<span class="detalhe"><span class="detalhe-num">' . absint($quartos) . '</span><span class="detalhe-label">Quartos</span></span>'; ?>
          <?php if ($banheiros) echo '<span class="detalhe"><span class="detalhe-num">' . absint($banheiros) . '</span><span class="detalhe-label">Banheiros</span></span>'; ?>
          <?php if ($vagas)     echo '<span class="detalhe"><span class="detalhe-num">' . absint($vagas) . '</span><span class="detalhe-label">Vagas</span></span>'; ?>
        </div>
        <?php endif; ?>
      </div>
    </div>
    <?php endwhile; wp_reset_postdata(); ?>
  </div>
  ... rodapé da seção (ver-todos) ...
</section>
<?php endif; ?>
```

Quando não há imóveis publicados, a seção inteira é omitida (condicional `if ($imoveis->have_posts())`).

### Busca

Manter `.busca-section` com `display: none` no CSS. Ativação em sessão separada com dados reais.

**Aceito quando:** criar post `imovel` no WP admin → aparece no card da home. Sem imóveis → seção oculta.

---

## 2.3 Responsividade Mobile

Breakpoint alvo: 375px (iPhone SE).
Breakpoints existentes no CSS:

- `@media (max-width: 1024px)` — tablet: já cobre `.hero`, `.hero-esquerda`, `.hero-direita`, `.hero-stats`, `.mr-nav`
- `@media (max-width: 768px)` — mobile: atualmente cobre apenas o header (hamburguer)

Os overrides abaixo são adicionados **dentro do bloco `@media (max-width: 768px)` existente**, complementando (não substituindo) os valores do breakpoint 1024px:

| Seletor | Problema em 375px | Override 768px |
|---|---|---|
| `.hero-esquerda` | padding lateral 40px → overflow | `padding: 100px 24px 60px` |
| `.hero-direita` | altura 400px → corte alto | `height: 260px` |
| `.hero-stats` | gap 30px → overflow horizontal | `gap: 16px; padding: 24px 24px` |
| `.imoveis-grid` | 3 colunas → cards minúsculos | `grid-template-columns: 1fr` |
| ~~`.busca-section`~~ | mantida `display: none` — sem override mobile necessário | — |
| `.sobre-section` | grid 2 col → comprimido | `grid-template-columns: 1fr; padding: 60px 24px` |
| `.sobre-foto` | min-height 500px → muito alto | `min-height: 280px` |
| `.captacao-section` | grid 2 col | `grid-template-columns: 1fr; padding: 60px 24px` |
| `.cta-section` | padding 100px 60px | `padding: 60px 24px` |
| `.mr-footer` | grid 4 col → overflow | `padding: 60px 24px 40px` |
| `.mr-footer-grid` | grid 4 col | `grid-template-columns: 1fr; gap: 40px` |
| `.mr-footer-bottom` | flex row → overflow | `flex-direction: column; gap: 16px; text-align: center` |

Nota: `.mr-footer-grid` não possui regra desktop em `main.css` (somente em `css_append.txt` não deployado). Adicionar regra desktop junto com o override mobile:
- Desktop base: `.mr-footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 60px; margin-bottom: 60px; }`
- Mobile override: dentro do `@media (max-width: 768px)` como na tabela acima

**Aceito quando:** sem overflow horizontal em 375px verificado via DevTools (document.body.scrollWidth === 375).

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `functions.php` | og:image + twitter:image em `marcos_rosa_seo_meta()` + CPT `imovel` + meta box + save handler |
| `front-page.php` | WP_Query condicional na seção de imóveis |
| `assets/css/main.css` | Base desktop `.mr-footer-grid` + overrides mobile em `@media (max-width: 768px)` |
