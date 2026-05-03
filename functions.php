<?php
/**
 * Marcos Rosa Corretor — functions.php v2.0.0
 * CRECI-GO 35088-F
 * WhatsApp fix + SMTP
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
        ['google-fonts'], '2.0.0'
    );
    // JS principal
    wp_enqueue_script('marcos-rosa-main',
        get_template_directory_uri() . '/assets/js/main.js',
        [], '2.1.0', true
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
    error_log('MR_CAPTACAO: ' . print_r($_POST, true));
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
    $msg      = rawurlencode("Olá Marcos! Meu nome é {$nome}, tenho um {$tipo} em {$bairro} para anunciar. Valor pretendido: R$ {$valor}. Pode me ajudar?");
    $wpp_link = "https://api.whatsapp.com/send?phone=5562981148448&text={$msg}";

    wp_send_json_success([
        'msg'      => 'Recebido! Marcos Rosa entrará em contato em breve.',
        'wpp_link' => $wpp_link,
    ]);
}
add_action('wp_ajax_marcos_rosa_captacao', 'marcos_rosa_captacao');
add_action('wp_ajax_nopriv_marcos_rosa_captacao', 'marcos_rosa_captacao');

// ─── SMTP CONFIG ────────────────────────────────────────────
function marcos_rosa_smtp( $phpmailer ) {
    $phpmailer->isSMTP();
    $phpmailer->Host       = 'smtp.imovflow.com.br';
    $phpmailer->SMTPAuth   = true;
    $phpmailer->Port       = 587;
    $phpmailer->SMTPSecure = 'tls';
    $phpmailer->Username   = 'contato@imovflow.com.br';
    $phpmailer->Password   = 'Imov2026';
    $phpmailer->From       = 'contato@imovflow.com.br';
    $phpmailer->FromName   = 'IMOVFLOW — Captação';
}
add_action( 'phpmailer_init', 'marcos_rosa_smtp' );

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
        'show_in_rest'    => true,
        'menu_icon'       => 'dashicons-building',
        'rewrite'         => ['slug' => 'imoveis', 'with_front' => false],
        'has_archive'     => true,
        'supports'        => ['title', 'editor', 'thumbnail'],
        'capability_type' => 'post',
    ]);
}
add_action('init', 'marcos_rosa_cpt_imovel');

// ─── TAXONOMIA: TIPO DE NEGÓCIO ─────────────────────────────
function marcos_rosa_tax_tipo_negocio() {
    register_taxonomy('tipo_negocio', 'imovel', [
        'labels' => [
            'name'          => 'Tipos de Negócio',
            'singular_name' => 'Tipo de Negócio',
            'add_new_item'  => 'Adicionar Tipo de Negócio',
            'search_items'  => 'Buscar Tipo de Negócio',
        ],
        'hierarchical'      => false,
        'public'            => true,
        'show_in_rest'      => true,
        'show_admin_column' => true,
        'rewrite'           => ['slug' => 'tipo-negocio'],
    ]);
}
add_action('init', 'marcos_rosa_tax_tipo_negocio');

// ─── META BOX: IMOVEL ───────────────────────────────────────
function marcos_rosa_imovel_meta_box_register() {
    add_meta_box(
        'marcos_rosa_imovel_detalhes',
        'Detalhes do Imóvel',
        'marcos_rosa_imovel_meta_box',
        'imovel',
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'marcos_rosa_imovel_meta_box_register');

function marcos_rosa_imovel_meta_box($post) {
    wp_nonce_field('marcos_rosa_save_imovel', 'marcos_rosa_imovel_nonce');
    $tipo       = get_post_meta($post->ID, '_imovel_tipo',       true);
    $finalidade = get_post_meta($post->ID, '_imovel_finalidade', true);
    $bairro     = get_post_meta($post->ID, '_imovel_bairro',     true);
    $valor      = get_post_meta($post->ID, '_imovel_valor',      true);
    $area       = get_post_meta($post->ID, '_imovel_area',       true);
    $quartos    = get_post_meta($post->ID, '_imovel_quartos',    true);
    $banheiros  = get_post_meta($post->ID, '_imovel_banheiros',  true);
    $vagas      = get_post_meta($post->ID, '_imovel_vagas',      true);
    $badge      = get_post_meta($post->ID, '_imovel_badge',      true);
    ?>
    <table class="form-table">
      <tr>
        <th><label for="imovel_tipo">Tipo</label></th>
        <td>
          <select id="imovel_tipo" name="imovel_tipo">
            <option value="">— selecione —</option>
            <?php foreach (['Apartamento','Casa','Terreno','Comercial'] as $opt): ?>
              <option value="<?php echo esc_attr($opt); ?>" <?php selected($tipo, $opt); ?>><?php echo esc_html($opt); ?></option>
            <?php endforeach; ?>
          </select>
        </td>
      </tr>
      <tr>
        <th><label for="imovel_finalidade">Finalidade</label></th>
        <td>
          <select id="imovel_finalidade" name="imovel_finalidade">
            <option value="">— selecione —</option>
            <?php foreach (['Venda','Aluguel'] as $opt): ?>
              <option value="<?php echo esc_attr($opt); ?>" <?php selected($finalidade, $opt); ?>><?php echo esc_html($opt); ?></option>
            <?php endforeach; ?>
          </select>
        </td>
      </tr>
      <tr>
        <th><label for="imovel_bairro">Bairro</label></th>
        <td><input type="text" id="imovel_bairro" name="imovel_bairro" value="<?php echo esc_attr($bairro); ?>" placeholder="ex: Jundiaí" class="regular-text"></td>
      </tr>
      <tr>
        <th><label for="imovel_valor">Valor (R$)</label></th>
        <td><input type="text" id="imovel_valor" name="imovel_valor" value="<?php echo esc_attr($valor); ?>" placeholder="ex: 350.000" class="regular-text"></td>
      </tr>
      <tr>
        <th><label for="imovel_area">Área (m²)</label></th>
        <td><input type="text" id="imovel_area" name="imovel_area" value="<?php echo esc_attr($area); ?>" placeholder="ex: 85" class="regular-text"></td>
      </tr>
      <tr>
        <th><label for="imovel_quartos">Quartos</label></th>
        <td><input type="number" id="imovel_quartos" name="imovel_quartos" value="<?php echo esc_attr($quartos); ?>" min="0" class="small-text"></td>
      </tr>
      <tr>
        <th><label for="imovel_banheiros">Banheiros</label></th>
        <td><input type="number" id="imovel_banheiros" name="imovel_banheiros" value="<?php echo esc_attr($banheiros); ?>" min="0" class="small-text"></td>
      </tr>
      <tr>
        <th><label for="imovel_vagas">Vagas</label></th>
        <td><input type="number" id="imovel_vagas" name="imovel_vagas" value="<?php echo esc_attr($vagas); ?>" min="0" class="small-text"></td>
      </tr>
      <tr>
        <th><label for="imovel_badge">Badge</label></th>
        <td><input type="text" id="imovel_badge" name="imovel_badge" value="<?php echo esc_attr($badge); ?>" placeholder="ex: LANÇAMENTO" class="regular-text"></td>
      </tr>
    </table>
    <?php
}

function marcos_rosa_save_imovel_meta($post_id) {
    if ( defined('DOING_AUTOSAVE') && DOING_AUTOSAVE )           return $post_id;
    if ( ! isset($_POST['marcos_rosa_imovel_nonce']) )           return $post_id;
    if ( ! wp_verify_nonce($_POST['marcos_rosa_imovel_nonce'],
                           'marcos_rosa_save_imovel') )          return $post_id;
    if ( ! current_user_can('edit_post', $post_id) )             return $post_id;

    $campos_texto = ['imovel_tipo','imovel_finalidade','imovel_bairro','imovel_valor','imovel_area','imovel_badge'];
    foreach ($campos_texto as $campo) {
        if (isset($_POST[$campo])) {
            update_post_meta($post_id, '_' . $campo, sanitize_text_field($_POST[$campo]));
        }
    }
    $campos_num = ['imovel_quartos','imovel_banheiros','imovel_vagas'];
    foreach ($campos_num as $campo) {
        if (isset($_POST[$campo])) {
            update_post_meta($post_id, '_' . $campo, absint($_POST[$campo]));
        }
    }
    return $post_id;
}
add_action('save_post_imovel', 'marcos_rosa_save_imovel_meta');

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
<meta property="og:image"        content="<?php echo esc_url(get_template_directory_uri() . '/assets/img/logo.png'); ?>">
<meta property="og:image:width"  content="512">
<meta property="og:image:height" content="512">
<meta name="twitter:image"       content="<?php echo esc_url(get_template_directory_uri() . '/assets/img/logo.png'); ?>">
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

