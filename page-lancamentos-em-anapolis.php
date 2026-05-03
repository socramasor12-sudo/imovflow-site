<?php
/**
 * Template: Lançamentos em Anápolis
 * Ativado automaticamente via slug matching (page-{slug}.php)
 * Página ID 110
 */
get_header();
?>

<!-- Hero -->
<section style="background-color: var(--azul); padding: 72px 24px 56px; text-align: center;">
    <p class="section-tag" style="color: var(--dourado); margin-bottom: 12px;">Novidades</p>
    <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 5vw, 3.2rem); color: var(--branco); margin: 0 0 14px;">
        Lançamentos em <span style="color: var(--dourado); font-style: italic;">Anápolis/GO</span>
    </h1>
    <p style="font-family: 'Josefin Sans', sans-serif; font-size: 1rem; color: rgba(255,255,255,0.75); letter-spacing: 0.08em; text-transform: uppercase; margin: 0;">
        Empreendimentos novos direto das construtoras
    </p>
</section>

<!-- Conteúdo editável pelo Admin (post_content) -->
<?php while ( have_posts() ) : the_post(); ?>
<?php if ( get_the_content() ) : ?>
<section style="background-color: #fff; padding: 48px 24px 32px;">
    <div style="max-width: 800px; margin: 0 auto; font-family: 'Josefin Sans', sans-serif; font-size: 0.85rem; font-weight: 300; line-height: 2; color: rgba(26,39,68,0.7); letter-spacing: 0.5px;">
        <?php the_content(); ?>
    </div>
</section>
<?php endif; ?>
<?php endwhile; ?>

<!-- Grid de Imóveis filtrado por taxonomia -->
<?php
$query_args = [
    'post_type'      => 'imovel',
    'posts_per_page' => 24,
    'post_status'    => 'publish',
    'orderby'        => 'date',
    'order'          => 'DESC',
    'tax_query'      => [[
        'taxonomy' => 'tipo_negocio',
        'field'    => 'slug',
        'terms'    => 'lancamentos',
    ]],
];
$imoveis_query = new WP_Query( $query_args );
?>

<section style="background-color: var(--background, #f8f6f1); padding: 60px 24px 80px;">
    <div style="max-width: 1200px; margin: 0 auto;">

        <?php if ( $imoveis_query->have_posts() ) : ?>
            <div class="imoveis-grid">
                <?php while ( $imoveis_query->have_posts() ) : $imoveis_query->the_post(); ?>
                    <?php get_template_part( 'template-parts/card-imovel' ); ?>
                <?php endwhile; ?>
            </div>
        <?php else : ?>
            <div style="text-align: center; padding: 80px 24px;">
                <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; color: var(--azul); margin-bottom: 20px;">
                    Nenhum lançamento disponível no momento.
                </p>
                <a href="https://wa.me/5562981148448"
                   class="btn-primary" target="_blank" rel="noopener noreferrer"
                   style="display: inline-block; background-color: var(--dourado); color: #fff; font-family: 'Josefin Sans', sans-serif; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; padding: 14px 36px; border-radius: 2px;">
                    Fale com Marcos Rosa
                </a>
            </div>
        <?php endif; ?>

        <?php wp_reset_postdata(); ?>
    </div>
</section>

<?php get_footer(); ?>
