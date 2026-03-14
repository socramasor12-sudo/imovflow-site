<?php
/**
 * Marcos Rosa Corretor — functions.php
 * CRECI-GO 35088-F
 */

// ─── SETUP ──────────────────────────────────────────────────
function marcos_rosa_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'comment-form', 'gallery', 'caption']);
    register_nav_menus(['primary' => 'Menu Principal']);
}
add_action('after_setup_theme', 'marcos_rosa_setup');

// ─── ENQUEUE SCRIPTS & STYLES ───────────────────────────────
function marcos_rosa_scripts() {
    // Google Fonts
    wp_enqueue_style('google-fonts',
        'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&family=Josefin+Sans:wght@200;300;400;600&display=swap',
        [], null
    );
    // CSS principal
    wp_enqueue_style('marcos-rosa-main',
        get_template_directory_uri() . '/assets/css/main.css',
        ['google-fonts'], '1.0.0'
    );
    // JS principal
    wp_enqueue_script('marcos-rosa-main',
        get_template_directory_uri() . '/assets/js/main.js',
        [], '1.0.0', true
    );

    // Passa variáveis para o JS
    wp_localize_script('marcos-rosa-main', 'marcosRosa', [
        'ajaxurl'   => admin_url('admin-ajax.php'),
        'nonce'     => wp_create_nonce('marcos_rosa_nonce'),
        'whatsapp'  => '5562981148448',
        'siteurl'   => get_site_url(),
    ]);
}
add_action('wp_enqueue_scripts', 'marcos_rosa_scripts');

// ─── CAPTAÇÃO — AJAX HANDLER ────────────────────────────────
function marcos_rosa_captacao() {
    check_ajax_referer('marcos_rosa_nonce', 'nonce');

    $nome    = sanitize_text_field($_POST['nome'] ?? '');
    $wpp     = sanitize_text_field($_POST['whatsapp'] ?? '');
    $tipo    = sanitize_text_field($_POST['tipo'] ?? '');
    $bairro  = sanitize_text_field($_POST['localizacao'] ?? $_POST['bairro'] ?? '');
    $valor   = sanitize_text_field($_POST['valor'] ?? '');

    if (empty($nome) || empty($wpp)) {
        wp_send_json_error(['msg' => 'Preencha nome e WhatsApp.']);
        return;
    }

    // Salva como post customizado
    $post_id = wp_insert_post([
        'post_type'   => 'captacao',
        'post_title'  => "Captação: {$nome} — {$tipo} em {$bairro}",
        'post_status' => 'publish',
        'meta_input'  => [
            '_captacao_nome'    => $nome,
            '_captacao_wpp'     => $wpp,
            '_captacao_tipo'    => $tipo,
            '_captacao_bairro'  => $bairro,
            '_captacao_valor'   => $valor,
            '_captacao_data'    => current_time('mysql'),
        ]
    ]);

    // Envia email de notificação
    $assunto = "Novo imóvel para captar: {$tipo} em {$bairro}";
    $mensagem = "Nome: {$nome}\nWhatsApp: {$wpp}\nTipo: {$tipo}\nBairro: {$bairro}\nValor: R$ {$valor}";
    wp_mail('mrcimoveis78@gmail.com', $assunto, $mensagem);

    // Link WhatsApp para contato imediato
    $wpp_limpo = preg_replace('/\D/', '', $wpp);
    $wpp_link  = "https://wa.me/55{$wpp_limpo}?text=" . urlencode("Olá {$nome}! Sou Marcos Rosa, Corretor Imobiliário CRECI-GO 35088-F. Vi que você tem um {$tipo} em {$bairro} para vender. Podemos conversar?");

    wp_send_json_success([
        'msg'      => 'Recebido! Marcos Rosa entrará em contato em breve.',
        'wpp_link' => $wpp_link,
    ]);
}
add_action('wp_ajax_marcos_rosa_captacao', 'marcos_rosa_captacao');
add_action('wp_ajax_nopriv_marcos_rosa_captacao', 'marcos_rosa_captacao');

// ─── CPT: CAPTACAO ──────────────────────────────────────────
function marcos_rosa_cpt() {
    register_post_type('captacao', [
        'label'               => 'Captações',
        'public'              => false,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'menu_icon'           => 'dashicons-building',
        'supports'            => ['title'],
        'capability_type'     => 'post',
    ]);
}
add_action('init', 'marcos_rosa_cpt');

// ─── CPT: IMOVEL ────────────────────────────────────────────
function marcos_rosa_cpt_imovel() {
    register_post_type('imovel', [
        'label'           => 'Imóveis',
        'public'          => true,
        'show_ui'         => true,
        'show_in_menu'    => true,
        'menu_icon'       => 'dashicons-admin-home',
        'rewrite'         => ['slug' => 'imoveis', 'with_front' => false],
        'has_archive'     => true,
        'supports'        => ['title', 'thumbnail'],
        'capability_type' => 'post',
    ]);
}
add_action('init', 'marcos_rosa_cpt_imovel');

// ─── IDENTIDADE Marcos Rosa — Corretor Imobiliário ──────────
remove_action('wp_head', 'wp_generator');

// ─── TITLE TAG ──────────────────────────────────────────────
function marcos_rosa_document_title( $parts ) {
    if ( is_front_page() ) {
        $parts['title'] = 'Corretor de Imóveis em Anápolis/GO';
    }
    $parts['tagline'] = 'Marcos Rosa — Corretor Imobiliário | CRECI-GO 35088-F';
    return $parts;
}
add_filter( 'document_title_parts', 'marcos_rosa_document_title' );

// ─── SEO META TAGS ──────────────────────────────────────────
function marcos_rosa_seo_meta() {
    $descricao = 'Marcos Rosa — Corretor de Imóveis em Anápolis/GO. CRECI-GO 35088-F. Especialista em lançamentos e revendas residenciais. Atendimento via WhatsApp (62) 98114-8448.';
    $keywords  = 'corretor de imóveis Anápolis, imóveis Anápolis GO, lançamentos imobiliários Anápolis, Marcos Rosa Corretor, CRECI-GO 35088-F, comprar imóvel Anápolis, revendas Anápolis';
    $titulo    = is_front_page()
        ? 'Corretor de Imóveis em Anápolis/GO | Marcos Rosa — CRECI-GO 35088-F'
        : get_the_title() . ' | Marcos Rosa — Corretor de Imóveis em Anápolis';
    ?>
<meta name="description" content="<?php echo esc_attr($descricao); ?>">
<meta name="keywords"    content="<?php echo esc_attr($keywords); ?>">
<meta name="author"      content="Marcos Rosa — Corretor Imobiliário | CRECI-GO 35088-F">
<meta name="robots"      content="index, follow">
<!-- Open Graph -->
<meta property="og:type"        content="website">
<meta property="og:locale"      content="pt_BR">
<meta property="og:site_name"   content="Marcos Rosa — Corretor Imobiliário">
<meta property="og:title"       content="<?php echo esc_attr($titulo); ?>">
<meta property="og:description" content="<?php echo esc_attr($descricao); ?>">
<meta property="og:url"         content="<?php echo esc_url(home_url('/')); ?>">
<meta property="og:image"        content="<?php echo esc_url(get_template_directory_uri()); ?>/assets/img/logo.png">
<meta property="og:image:width"  content="512">
<meta property="og:image:height" content="512">
<meta name="twitter:image"       content="<?php echo esc_url(get_template_directory_uri()); ?>/assets/img/logo.png">
<!-- Twitter Card -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="<?php echo esc_attr($titulo); ?>">
<meta name="twitter:description" content="<?php echo esc_attr($descricao); ?>">
<!-- Contato estruturado -->
<meta name="contact:whatsapp"   content="+55 (62) 98114-8448">
<meta name="contact:creci"      content="CRECI-GO 35088-F">
    <?php
}
add_action( 'wp_head', 'marcos_rosa_seo_meta', 1 );
