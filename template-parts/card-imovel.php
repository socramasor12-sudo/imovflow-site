<?php
$categoria = get_post_meta( get_the_ID(), '_imovel_categoria', true );
$preco     = get_post_meta( get_the_ID(), '_imovel_preco',     true );
$bairro    = get_post_meta( get_the_ID(), '_imovel_bairro',    true );
$tipo      = get_post_meta( get_the_ID(), '_imovel_tipo',      true );
$quartos   = get_post_meta( get_the_ID(), '_imovel_quartos',   true );
$vagas     = get_post_meta( get_the_ID(), '_imovel_vagas',     true );

$preco_formatado = $preco
    ? 'R$ ' . number_format( (float) $preco, 0, ',', '.' )
    : 'Consulte';
?>

<article class="card-imovel" id="imovel-<?php the_ID(); ?>">

    <a href="<?php the_permalink(); ?>" class="card-thumb">
        <?php if ( has_post_thumbnail() ) : ?>
            <?php the_post_thumbnail( 'medium_large', array( 'alt' => get_the_title(), 'loading' => 'lazy' ) ); ?>
        <?php else : ?>
            <div class="card-thumb-placeholder">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                    <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
                    <path d="M9 21V12h6v9"/>
                </svg>
            </div>
        <?php endif; ?>

        <?php if ( $categoria ) : ?>
            <span class="card-badge"><?php echo esc_html( ucfirst( $categoria ) ); ?></span>
        <?php endif; ?>
    </a>

    <div class="card-body">
        <p class="card-tipo"><?php echo esc_html( $tipo ?: 'Imóvel' ); ?></p>
        <h3 class="card-title">
            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
        </h3>

        <?php if ( $bairro ) : ?>
            <p class="card-bairro">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                </svg>
                <?php echo esc_html( $bairro ); ?> &ndash; Anápolis/GO
            </p>
        <?php endif; ?>

        <div class="card-features">
            <?php if ( $quartos ) : ?>
                <span class="feature">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                        <path d="M3 9V19h18V9M3 9l9-6 9 6"/>
                    </svg>
                    <?php echo esc_html( $quartos ); ?> quarto<?php echo $quartos > 1 ? 's' : ''; ?>
                </span>
            <?php endif; ?>
            <?php if ( $vagas ) : ?>
                <span class="feature">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                        <rect x="1" y="3" width="15" height="13" rx="1"/>
                        <path d="M16 8h4l3 3v4h-7V8z"/>
                        <circle cx="5.5" cy="18.5" r="2.5"/>
                        <circle cx="18.5" cy="18.5" r="2.5"/>
                    </svg>
                    <?php echo esc_html( $vagas ); ?> vaga<?php echo $vagas > 1 ? 's' : ''; ?>
                </span>
            <?php endif; ?>
        </div>

        <div class="card-footer">
            <p class="card-preco"><?php echo esc_html( $preco_formatado ); ?></p>
            <a
                href="https://wa.me/5562981148448?text=<?php echo urlencode( 'Olá Marcos! Vi o imóvel "' . get_the_title() . '" no site e gostaria de mais informações.' ); ?>"
                class="btn-card-whatsapp"
                target="_blank"
                rel="noopener noreferrer"
            >
                Tenho interesse
            </a>
        </div>
    </div>

</article>
