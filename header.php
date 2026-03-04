<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<?php wp_head(); ?>
<!-- Schema.org: Marcos Rosa — Corretor Imobiliário -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "name": "Marcos Rosa — Corretor Imobiliário",
  "description": "Corretor de Imóveis em Anápolis/GO. CRECI-GO 35088-F. Especialista em lançamentos e revendas residenciais.",
  "url": "<?php echo esc_url(home_url('/')); ?>",
  "telephone": "+55 62 98114-8448",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Anápolis",
    "addressRegion": "GO",
    "addressCountry": "BR"
  },
  "identifier": "CRECI-GO 35088-F",
  "sameAs": []
}
</script>
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
