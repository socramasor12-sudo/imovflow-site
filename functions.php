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
    $bairro  = sanitize_text_field($_POST['bairro'] ?? '');
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

// ─── REMOVE IMOVFLOW BRANDING ───────────────────────────────
remove_action('wp_head', 'wp_generator');

// ─── TITLE TAG ──────────────────────────────────────────────
function marcos_rosa_wp_title($title) {
    return $title . ' | Marcos Rosa — Corretor Imobiliário CRECI-GO 35088-F';
}
