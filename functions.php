<?php

function marcos_rosa_setup() {
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );

    register_nav_menus( array(
        'primary' => __( 'Menu Principal', 'marcos-rosa' ),
    ) );
}
add_action( 'after_setup_theme', 'marcos_rosa_setup' );


function marcos_rosa_enqueue() {
    wp_enqueue_style(
        'google-fonts',
        'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Josefin+Sans:wght@300;400;600&display=swap',
        array(),
        null
    );

    wp_enqueue_style(
        'marcos-rosa-main',
        get_template_directory_uri() . '/assets/css/main.css',
        array( 'google-fonts' ),
        '1.0.0'
    );

    wp_enqueue_script(
        'marcos-rosa-main',
        get_template_directory_uri() . '/assets/js/main.js',
        array(),
        '1.0.0',
        true
    );

    wp_localize_script( 'marcos-rosa-main', 'marcosRosa', array(
        'ajaxurl' => admin_url( 'admin-ajax.php' ),
        'nonce'   => wp_create_nonce( 'captacao_nonce' ),
    ) );
}
add_action( 'wp_enqueue_scripts', 'marcos_rosa_enqueue' );


function marcos_rosa_register_imovel() {
    $labels = array(
        'name'          => 'Imóveis',
        'singular_name' => 'Imóvel',
        'add_new_item'  => 'Adicionar Imóvel',
        'edit_item'     => 'Editar Imóvel',
    );

    register_post_type( 'imovel', array(
        'labels'      => $labels,
        'public'      => true,
        'has_archive' => true,
        'supports'    => array( 'title', 'editor', 'thumbnail', 'custom-fields' ),
        'menu_icon'   => 'dashicons-building',
        'rewrite'     => array( 'slug' => 'imoveis' ),
    ) );
}
add_action( 'init', 'marcos_rosa_register_imovel' );


function marcos_rosa_ajax_captacao() {
    check_ajax_referer( 'captacao_nonce', 'nonce' );

    $nome      = sanitize_text_field( $_POST['nome'] ?? '' );
    $telefone  = sanitize_text_field( $_POST['telefone'] ?? '' );
    $email     = sanitize_email( $_POST['email'] ?? '' );
    $endereco  = sanitize_text_field( $_POST['endereco'] ?? '' );
    $tipo      = sanitize_text_field( $_POST['tipo'] ?? '' );
    $mensagem  = sanitize_textarea_field( $_POST['mensagem'] ?? '' );

    if ( empty( $nome ) || empty( $telefone ) ) {
        wp_send_json_error( array( 'message' => 'Preencha os campos obrigatórios.' ) );
    }

    $post_id = wp_insert_post( array(
        'post_title'  => 'Captação - ' . $nome . ' - ' . date( 'd/m/Y H:i' ),
        'post_type'   => 'captacao',
        'post_status' => 'publish',
    ) );

    if ( $post_id ) {
        update_post_meta( $post_id, '_captacao_nome',     $nome );
        update_post_meta( $post_id, '_captacao_telefone', $telefone );
        update_post_meta( $post_id, '_captacao_email',    $email );
        update_post_meta( $post_id, '_captacao_endereco', $endereco );
        update_post_meta( $post_id, '_captacao_tipo',     $tipo );
        update_post_meta( $post_id, '_captacao_mensagem', $mensagem );
    }

    $subject = 'Nova Captação de Imóvel - ' . $nome;
    $body    = "Nome: $nome\nTelefone: $telefone\nE-mail: $email\nEndereço: $endereco\nTipo: $tipo\nMensagem: $mensagem";
    $headers = array( 'Content-Type: text/plain; charset=UTF-8' );

    wp_mail( 'mrcimoveis78@gmail.com', $subject, $body, $headers );

    wp_send_json_success( array( 'message' => 'Solicitação enviada com sucesso!' ) );
}
add_action( 'wp_ajax_captacao',        'marcos_rosa_ajax_captacao' );
add_action( 'wp_ajax_nopriv_captacao', 'marcos_rosa_ajax_captacao' );


function marcos_rosa_register_captacao() {
    register_post_type( 'captacao', array(
        'labels'      => array(
            'name'          => 'Captações',
            'singular_name' => 'Captação',
        ),
        'public'      => false,
        'show_ui'     => true,
        'supports'    => array( 'title', 'custom-fields' ),
        'menu_icon'   => 'dashicons-email-alt',
    ) );
}
add_action( 'init', 'marcos_rosa_register_captacao' );
