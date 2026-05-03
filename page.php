<?php
/**
 * page.php — Template para páginas genéricas (post_type=page)
 *
 * Necessário para que o Elementor e qualquer outra página do tipo 'page'
 * renderize corretamente. Sem este arquivo, o WordPress cai no index.php
 * que é "Silence is golden" e não renderiza nada.
 */
get_header(); ?>

<main id="main-content" class="page-content">
    <?php
    while ( have_posts() ) :
        the_post();
        the_content();
    endwhile;
    ?>
</main>

<?php get_footer(); ?>
