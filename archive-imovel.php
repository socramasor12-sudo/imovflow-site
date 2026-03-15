<?php
/**
 * Archive template for 'imovel' CPT
 * Theme: Marcos Rosa Corretor
 */

get_header();

// Sanitize and validate the 'finalidade' filter
$finalidade_raw   = isset( $_GET['finalidade'] ) ? sanitize_text_field( wp_unslash( $_GET['finalidade'] ) ) : '';
$allowed_finalidades = array( 'Venda', 'Aluguel' );
$finalidade = in_array( $finalidade_raw, $allowed_finalidades, true ) ? $finalidade_raw : '';

// Build WP_Query args
$query_args = array(
    'post_type'      => 'imovel',
    'posts_per_page' => 12,
    'post_status'    => 'publish',
    'orderby'        => 'date',
    'order'          => 'DESC',
    'paged'          => max( 1, get_query_var( 'paged' ) ),
);

if ( $finalidade ) {
    $query_args['meta_query'] = array(
        array(
            'key'     => '_imovel_finalidade',
            'value'   => $finalidade,
            'compare' => '=',
        ),
    );
}

$imoveis_query = new WP_Query( $query_args );
?>

<!-- Page Header -->
<section style="background-color: var(--azul); padding: 72px 24px 56px; text-align: center;">
    <p class="section-tag" style="color: var(--dourado); margin-bottom: 12px;">Portfólio</p>
    <h1 style="font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 5vw, 3.2rem); color: var(--branco); margin: 0 0 14px;">
        Todos os Imóveis
    </h1>
    <p style="font-family: 'Josefin Sans', sans-serif; font-size: 1rem; color: rgba(255,255,255,0.75); letter-spacing: 0.08em; text-transform: uppercase; margin: 0;">
        Lançamentos e Revendas em Anápolis/GO
    </p>
</section>

<!-- Filter Bar -->
<section style="background-color: #fff; border-bottom: 1px solid rgba(26,39,68,0.1); padding: 0 24px;">
    <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; gap: 8px; padding: 16px 0; flex-wrap: wrap;">
        <span style="font-family: 'Josefin Sans', sans-serif; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--azul); margin-right: 8px;">
            Filtrar por:
        </span>

        <?php
        $filters = array(
            ''        => 'Todos',
            'Venda'   => 'Venda',
            'Aluguel' => 'Aluguel',
        );

        foreach ( $filters as $value => $label ) :
            $is_active = ( $value === $finalidade );
            $href      = $value ? esc_url( add_query_arg( 'finalidade', $value, get_post_type_archive_link( 'imovel' ) ) ) : esc_url( get_post_type_archive_link( 'imovel' ) );

            $active_style = $is_active
                ? 'background-color: var(--dourado); color: #fff; border-color: var(--dourado);'
                : 'background-color: transparent; color: var(--azul); border-color: rgba(26,39,68,0.25);';
            ?>
            <a href="<?php echo $href; ?>"
               style="font-family: 'Josefin Sans', sans-serif; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; text-decoration: none; padding: 7px 20px; border: 1px solid; border-radius: 2px; transition: all 0.2s ease; <?php echo $active_style; ?>">
                <?php echo esc_html( $label ); ?>
            </a>
        <?php endforeach; ?>
    </div>
</section>

<!-- Listings Grid -->
<section style="background-color: var(--background, #f8f6f1); padding: 60px 24px 80px;">
    <div style="max-width: 1200px; margin: 0 auto;">

        <?php if ( $imoveis_query->have_posts() ) : ?>

            <div class="imoveis-grid">
                <?php while ( $imoveis_query->have_posts() ) : $imoveis_query->the_post(); ?>
                    <?php get_template_part( 'template-parts/card-imovel' ); ?>
                <?php endwhile; ?>
            </div>

            <?php
            // Pagination
            $pagination = paginate_links( array(
                'base'      => str_replace( 999999999, '%#%', esc_url( get_pagenum_link( 999999999 ) ) ),
                'format'    => '?paged=%#%',
                'current'   => max( 1, get_query_var( 'paged' ) ),
                'total'     => $imoveis_query->max_num_pages,
                'prev_text' => '&larr; Anterior',
                'next_text' => 'Próxima &rarr;',
                'type'      => 'list',
            ) );

            if ( $pagination ) : ?>
                <nav style="margin-top: 56px; text-align: center;" aria-label="Paginação de imóveis">
                    <style>
                        .imoveis-pagination ul { list-style: none; padding: 0; margin: 0; display: inline-flex; gap: 6px; flex-wrap: wrap; justify-content: center; }
                        .imoveis-pagination li a,
                        .imoveis-pagination li span { display: inline-block; padding: 8px 16px; font-family: 'Josefin Sans', sans-serif; font-size: 0.82rem; letter-spacing: 0.06em; text-decoration: none; border: 1px solid rgba(26,39,68,0.25); color: var(--azul); border-radius: 2px; transition: all 0.2s ease; }
                        .imoveis-pagination li a:hover { background-color: var(--azul); color: #fff; border-color: var(--azul); }
                        .imoveis-pagination li span.current { background-color: var(--dourado); color: #fff; border-color: var(--dourado); }
                    </style>
                    <div class="imoveis-pagination">
                        <?php echo $pagination; ?>
                    </div>
                </nav>
            <?php endif; ?>

        <?php else : ?>

            <!-- Empty State -->
            <div style="text-align: center; padding: 80px 24px;">
                <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; color: var(--azul); margin-bottom: 20px;">
                    Nenhum imóvel disponível no momento.
                </p>
                <a href="https://wa.me/5562981148448"
                   class="btn-primary"
                   target="_blank"
                   rel="noopener noreferrer"
                   style="display: inline-block; background-color: var(--dourado); color: #fff; font-family: 'Josefin Sans', sans-serif; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; padding: 14px 36px; border-radius: 2px;">
                    Fale com Marcos Rosa
                </a>
            </div>

        <?php endif; ?>

        <?php wp_reset_postdata(); ?>

    </div>
</section>

<?php get_footer(); ?>
