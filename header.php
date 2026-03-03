<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- HEADER -->
<header class="mr-header" id="mr-header">
  <a href="<?php echo esc_url(home_url('/')); ?>" class="mr-logo">
    <img src="<?php echo get_template_directory_uri(); ?>/assets/img/logo.png"
         alt="Marcos Rosa — Corretor Imobiliário CRECI-GO 35088-F">
  </a>

  <nav class="mr-nav">
    <a href="<?php echo home_url('/#imoveis'); ?>">Lançamentos</a>
    <a href="<?php echo home_url('/revendas'); ?>">Revendas</a>
    <a href="<?php echo home_url('/#vender'); ?>">Vender Imóvel</a>
    <a href="<?php echo home_url('/#sobre'); ?>">Sobre</a>
    <a href="<?php echo home_url('/#contato'); ?>">Contato</a>
  </nav>

  <a href="https://wa.me/5562981148448" class="mr-btn-wpp" target="_blank">
    💬 Fale Agora
  </a>

  <button class="mr-menu-toggle" id="mr-menu-toggle" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
</header>
