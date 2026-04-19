<?php
/**
 * Template para exibição individual de imóvel (CPT: imovel)
 * Marcos Rosa Corretor — CRECI-GO 35088-F
 * Layout profissional com hero, galeria, meta fields e CTA
 */
get_header();
?>

<?php while (have_posts()) : the_post();
    $post_id    = get_the_ID();
    $tipo       = get_post_meta($post_id, '_imovel_tipo',       true);
    $finalidade = get_post_meta($post_id, '_imovel_finalidade', true);
    $valor      = get_post_meta($post_id, '_imovel_valor',      true);
    $area       = get_post_meta($post_id, '_imovel_area',       true);
    $quartos    = get_post_meta($post_id, '_imovel_quartos',    true);
    $banheiros  = get_post_meta($post_id, '_imovel_banheiros',  true);
    $vagas      = get_post_meta($post_id, '_imovel_vagas',      true);
    $bairro     = get_post_meta($post_id, '_imovel_bairro',     true);
    $badge      = get_post_meta($post_id, '_imovel_badge',      true);

    // Formata valor: suporta "350000", "350.000", "350,000" → "R$ 350.000"
    $valor_fmt = '';
    if ($valor !== '' && $valor) {
        if (is_numeric(str_replace(['.', ','], '', $valor))) {
            $valor_numerico = (float) str_replace(['.', ','], ['', '.'], $valor);
            if (preg_match('/^\d{1,3}(\.\d{3})+$/', trim($valor))) {
                $valor_numerico = (float) str_replace('.', '', $valor);
            }
            $valor_fmt = 'R$ ' . number_format($valor_numerico, 0, ',', '.');
        } else {
            $valor_fmt = 'R$ ' . $valor;
        }
    }

    // Link WhatsApp com texto pré-preenchido
    $wpp_texto = 'Tenho interesse neste imóvel: ' . get_the_title();
    $wpp_link  = 'https://wa.me/5562981148448?text=' . rawurlencode($wpp_texto);

    // Foto principal (thumbnail do post)
    $thumb_url = '';
    if (has_post_thumbnail()) {
        $thumb_src = wp_get_attachment_image_src(get_post_thumbnail_id(), 'full');
        if ($thumb_src) {
            $thumb_url = $thumb_src[0];
        }
    }

    // Galeria: todos os attachments de imagem do post
    $fotos = get_posts([
        'post_type'      => 'attachment',
        'post_mime_type' => 'image',
        'posts_per_page' => -1,
        'post_parent'    => get_the_ID(),
        'orderby'        => 'menu_order',
        'order'          => 'ASC',
    ]);
?>

<style>
/* ─── SINGLE IMÓVEL — CSS INLINE ─────────────────────────────────────── */
:root {
    --azul: #1a2744;
    --dourado: #c9a84c;
    --dourado-escuro: #b8963e;
    --branco: #f8f6f1;
    --cinza-claro: rgba(26,39,68,0.08);
}

/* HERO */
.imovel-hero {
    position: relative;
    height: 500px;
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    display: flex;
    align-items: flex-end;
}
.imovel-hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(26,39,68,0.15) 0%,
        rgba(26,39,68,0.55) 60%,
        rgba(26,39,68,0.90) 100%
    );
    z-index: 1;
}
.imovel-hero-content {
    position: relative;
    z-index: 2;
    width: 100%;
    padding: 0 60px 48px;
}
.imovel-hero-badge {
    display: inline-block;
    background: var(--dourado);
    color: var(--azul);
    font-size: 0.55rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 6px 18px;
    border-radius: 2px;
    margin-bottom: 16px;
    font-weight: 600;
}
.imovel-hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1.8rem, 4vw, 3rem);
    font-weight: 300;
    color: var(--branco);
    line-height: 1.15;
    margin: 0 0 8px;
}
.imovel-hero-location {
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: rgba(248,246,241,0.65);
    text-transform: uppercase;
}

/* BARRA DE DETALHES */
.imovel-detalhes-bar {
    background: var(--azul);
    border-top: 1px solid rgba(201,168,76,0.25);
    padding: 28px 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
}
.imovel-detalhes-grupo {
    display: flex;
    align-items: center;
    gap: 28px;
    flex-wrap: wrap;
}
.imovel-detalhe-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    color: rgba(248,246,241,0.8);
    letter-spacing: 0.5px;
}
.imovel-detalhe-item .emoji {
    font-size: 1.2rem;
    line-height: 1;
}
.imovel-detalhe-item .label {
    font-size: 0.55rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(248,246,241,0.45);
    display: block;
}
.imovel-detalhe-item .valor-num {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--branco);
}
.imovel-preco-destaque {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 600;
    color: var(--dourado);
    letter-spacing: 1px;
}
.imovel-tags-inline {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.imovel-tag {
    background: rgba(201,168,76,0.12);
    border: 1px solid rgba(201,168,76,0.25);
    padding: 4px 14px;
    border-radius: 2px;
    font-size: 0.5rem;
    letter-spacing: 2px;
    color: rgba(248,246,241,0.65);
    text-transform: uppercase;
}

/* GALERIA */
.imovel-galeria-section {
    background: white;
    padding: 60px;
}
.imovel-galeria-header {
    max-width: 1200px;
    margin: 0 auto 32px;
}
.imovel-galeria-tag {
    font-size: 0.55rem;
    letter-spacing: 4px;
    color: var(--dourado-escuro);
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.imovel-galeria-tag::before {
    content: '';
    display: inline-block;
    width: 30px;
    height: 1px;
    background: var(--dourado);
}
.imovel-galeria-titulo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 300;
    color: var(--azul);
    margin: 0;
}
.imovel-galeria-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    max-width: 1200px;
    margin: 0 auto;
}
.imovel-galeria-item {
    position: relative;
    padding-top: 75%; /* aspect-ratio 4:3 */
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    overflow: hidden;
}
.imovel-galeria-item:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 32px rgba(26,39,68,0.18);
}
.imovel-galeria-item::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, transparent 60%, rgba(26,39,68,0.25) 100%);
    border-radius: 8px;
    opacity: 0;
    transition: opacity 0.3s ease;
}
.imovel-galeria-item:hover::after {
    opacity: 1;
}

/* DESCRIÇÃO */
.imovel-descricao-section {
    background: white;
    border-top: 1px solid var(--cinza-claro);
    padding: 60px;
}
.imovel-descricao-inner {
    max-width: 800px;
    margin: 0 auto;
}
.imovel-descricao-tag {
    font-size: 0.55rem;
    letter-spacing: 4px;
    color: var(--dourado-escuro);
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.imovel-descricao-tag::before {
    content: '';
    display: inline-block;
    width: 30px;
    height: 1px;
    background: var(--dourado);
}
.imovel-descricao-titulo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 300;
    color: var(--azul);
    margin: 0 0 32px;
}
.imovel-descricao-body {
    font-size: 0.8rem;
    font-weight: 300;
    letter-spacing: 1px;
    line-height: 2;
    color: rgba(26,39,68,0.75);
}
.imovel-descricao-body p {
    margin-bottom: 1.5em;
}

/* CTA INLINE */
.imovel-cta-inline {
    max-width: 800px;
    margin: 40px auto 0;
    text-align: center;
    padding: 40px;
    background: rgba(26,39,68,0.03);
    border-radius: 12px;
    border: 1px solid rgba(201,168,76,0.15);
}
.imovel-cta-inline .btn-wpp {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 18px 40px;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: var(--dourado);
    color: var(--azul);
    text-decoration: none;
    border-radius: 4px;
    font-weight: 600;
    transition: background 0.3s ease, transform 0.2s ease;
}
.imovel-cta-inline .btn-wpp:hover {
    background: var(--dourado-escuro);
    transform: translateY(-2px);
}

/* CTA FINAL (Fale com Marcos Rosa) */
.imovel-cta-final {
    background: var(--azul);
    padding: 80px 60px;
    text-align: center;
    border-top: 1px solid rgba(201,168,76,0.2);
}
.imovel-cta-final-inner {
    max-width: 600px;
    margin: 0 auto;
}
.imovel-cta-final .section-tag {
    font-size: 0.55rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(201,168,76,0.7);
    margin-bottom: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
}
.imovel-cta-final h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 300;
    color: var(--branco);
    margin: 0 0 12px;
    line-height: 1.2;
}
.imovel-cta-final h2 span {
    color: var(--dourado);
    font-style: italic;
}
.imovel-cta-final p {
    font-size: 0.7rem;
    font-weight: 300;
    letter-spacing: 1.5px;
    color: rgba(248,246,241,0.55);
    margin-bottom: 40px;
    line-height: 2;
}
.imovel-cta-final .btn-wpp-final {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 18px 48px;
    font-size: 0.65rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: var(--dourado);
    color: var(--azul);
    text-decoration: none;
    border-radius: 4px;
    font-weight: 600;
    transition: background 0.3s ease, transform 0.2s ease;
}
.imovel-cta-final .btn-wpp-final:hover {
    background: var(--dourado-escuro);
    transform: translateY(-2px);
}

/* LIGHTBOX */
.imovel-lightbox {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 99999;
    background: rgba(26,39,68,0.95);
    align-items: center;
    justify-content: center;
    cursor: pointer;
}
.imovel-lightbox.active {
    display: flex;
}
.imovel-lightbox-img {
    width: 90vw;
    height: 80vh;
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
    border-radius: 8px;
    box-shadow: 0 16px 64px rgba(0,0,0,0.4);
}
.imovel-lightbox-close {
    position: absolute;
    top: 24px;
    right: 32px;
    font-size: 2rem;
    color: var(--branco);
    background: none;
    border: none;
    cursor: pointer;
    z-index: 100000;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s;
}
.imovel-lightbox-close:hover {
    background: rgba(255,255,255,0.1);
}
.imovel-lightbox-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2.5rem;
    color: var(--branco);
    background: rgba(255,255,255,0.1);
    border: none;
    cursor: pointer;
    z-index: 100000;
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s;
}
.imovel-lightbox-nav:hover {
    background: rgba(255,255,255,0.2);
}
.imovel-lightbox-prev {
    left: 24px;
}
.imovel-lightbox-next {
    right: 24px;
}
.imovel-lightbox-counter {
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(248,246,241,0.6);
    font-size: 0.75rem;
    letter-spacing: 2px;
}

/* RESPONSIVO */
@media (max-width: 768px) {
    .imovel-hero {
        height: 300px;
    }
    .imovel-hero-content {
        padding: 0 24px 32px;
    }
    .imovel-hero-title {
        font-size: 1.6rem;
    }
    .imovel-detalhes-bar {
        padding: 20px 24px;
        flex-direction: column;
        align-items: flex-start;
    }
    .imovel-detalhes-grupo {
        gap: 16px;
    }
    .imovel-galeria-section {
        padding: 40px 24px;
    }
    .imovel-galeria-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
    }
    .imovel-descricao-section {
        padding: 40px 24px;
    }
    .imovel-descricao-titulo {
        font-size: 1.4rem;
    }
    .imovel-descricao-body {
        font-size: 0.75rem;
        letter-spacing: 0.3px;
        line-height: 1.8;
    }
    .imovel-cta-final {
        padding: 60px 24px;
    }
    .imovel-lightbox-nav {
        width: 40px;
        height: 40px;
        font-size: 1.5rem;
    }
    .imovel-lightbox-prev {
        left: 8px;
    }
    .imovel-lightbox-next {
        right: 8px;
    }
}
</style>

<!-- ─── HERO COM FOTO PRINCIPAL ──────────────────────────────────────── -->
<section class="imovel-hero" style="background-image: url('<?php echo esc_url($thumb_url); ?>');">
    <div class="imovel-hero-overlay"></div>
    <div class="imovel-hero-content">
        <?php if ($badge) : ?>
            <div class="imovel-hero-badge"><?php echo esc_html($badge); ?></div>
        <?php endif; ?>
        <h1 class="imovel-hero-title"><?php the_title(); ?></h1>
        <?php if ($bairro) : ?>
            <div class="imovel-hero-location">📍 <?php echo esc_html($bairro); ?> — Anápolis/GO</div>
        <?php endif; ?>
    </div>
</section>

<!-- ─── BARRA DE DETALHES ────────────────────────────────────────────── -->
<section class="imovel-detalhes-bar">
    <div class="imovel-detalhes-grupo">
        <?php if ($valor_fmt) : ?>
            <div class="imovel-preco-destaque"><?php echo esc_html($valor_fmt); ?></div>
        <?php endif; ?>

        <div class="imovel-tags-inline">
            <?php if ($tipo) : ?>
                <span class="imovel-tag"><?php echo esc_html($tipo); ?></span>
            <?php endif; ?>
            <?php if ($finalidade) : ?>
                <span class="imovel-tag"><?php echo esc_html($finalidade); ?></span>
            <?php endif; ?>
        </div>
    </div>

    <div class="imovel-detalhes-grupo">
        <?php if ($quartos) : ?>
            <div class="imovel-detalhe-item">
                <span class="emoji">🛏</span>
                <div>
                    <span class="valor-num"><?php echo absint($quartos); ?></span>
                    <span class="label">Quartos</span>
                </div>
            </div>
        <?php endif; ?>

        <?php if ($banheiros) : ?>
            <div class="imovel-detalhe-item">
                <span class="emoji">🚿</span>
                <div>
                    <span class="valor-num"><?php echo absint($banheiros); ?></span>
                    <span class="label">Banheiros</span>
                </div>
            </div>
        <?php endif; ?>

        <?php if ($vagas) : ?>
            <div class="imovel-detalhe-item">
                <span class="emoji">🚗</span>
                <div>
                    <span class="valor-num"><?php echo absint($vagas); ?></span>
                    <span class="label">Vagas</span>
                </div>
            </div>
        <?php endif; ?>

        <?php if ($area) : ?>
            <div class="imovel-detalhe-item">
                <span class="emoji">📐</span>
                <div>
                    <span class="valor-num"><?php echo esc_html($area); ?> m²</span>
                    <span class="label">Área</span>
                </div>
            </div>
        <?php endif; ?>
    </div>
</section>

<!-- ─── GALERIA DE FOTOS ─────────────────────────────────────────────── -->
<?php if (!empty($fotos)) : ?>
<section class="imovel-galeria-section">
    <div class="imovel-galeria-header">
        <div class="imovel-galeria-tag">Galeria de Fotos</div>
        <h2 class="imovel-galeria-titulo">Conheça cada detalhe</h2>
    </div>
    <div class="imovel-galeria-grid">
        <?php foreach ($fotos as $index => $foto) :
            $foto_src = wp_get_attachment_image_src($foto->ID, 'full');
            $foto_full = wp_get_attachment_image_src($foto->ID, 'full');
            if ($foto_src) :
        ?>
            <div class="imovel-galeria-item"
                 style="background-image: url('<?php echo esc_url($foto_src[0]); ?>');"
                 data-full="<?php echo esc_url($foto_full ? $foto_full[0] : $foto_src[0]); ?>"
                 data-index="<?php echo $index; ?>"
                 onclick="imovelLightbox.open(this)"
                 role="button"
                 tabindex="0"
                 aria-label="Ver foto <?php echo ($index + 1); ?> em tamanho grande">
            </div>
        <?php
            endif;
        endforeach; ?>
    </div>
</section>
<?php endif; ?>

<!-- ─── DESCRIÇÃO COMPLETA ───────────────────────────────────────────── -->
<?php if (get_the_content()) : ?>
<section class="imovel-descricao-section">
    <div class="imovel-descricao-inner">
        <div class="imovel-descricao-tag">Descrição</div>
        <h2 class="imovel-descricao-titulo">Sobre este imóvel</h2>
        <div class="imovel-descricao-body entry-content">
            <?php the_content(); ?>
        </div>

        <!-- CTA inline -->
        <div class="imovel-cta-inline">
            <a href="<?php echo esc_url($wpp_link); ?>"
               target="_blank"
               rel="noopener noreferrer"
               class="btn-wpp">
                💬 Tenho interesse neste imóvel
            </a>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- ─── FALE COM MARCOS ROSA ─────────────────────────────────────────── -->
<section class="imovel-cta-final">
    <div class="imovel-cta-final-inner">
        <div class="section-tag">Pronto para dar o próximo passo?</div>
        <h2>Fale com <span>Marcos Rosa</span></h2>
        <p>Corretor de Imóveis · CRECI-GO 35088-F · Atendimento 7 dias por semana</p>
        <a href="<?php echo esc_url($wpp_link); ?>"
           target="_blank"
           rel="noopener noreferrer"
           class="btn-wpp-final">
            💬 Tenho interesse neste imóvel
        </a>
    </div>
</section>

<!-- ─── LIGHTBOX ──────────────────────────────────────────────────────── -->
<div class="imovel-lightbox" id="imovelLightbox">
    <button class="imovel-lightbox-close" onclick="imovelLightbox.close()" aria-label="Fechar">✕</button>
    <button class="imovel-lightbox-nav imovel-lightbox-prev" onclick="imovelLightbox.prev()" aria-label="Anterior">‹</button>
    <div class="imovel-lightbox-img" id="imovelLightboxImg" style="width:90vw;height:80vh;background-size:contain;background-position:center;background-repeat:no-repeat;border-radius:8px;"></div>
    <button class="imovel-lightbox-nav imovel-lightbox-next" onclick="imovelLightbox.next()" aria-label="Próxima">›</button>
    <div class="imovel-lightbox-counter" id="imovelLightboxCounter"></div>
</div>

<script>
(function() {
    var lightbox = {
        el: document.getElementById('imovelLightbox'),
        img: document.getElementById('imovelLightboxImg'),
        counter: document.getElementById('imovelLightboxCounter'),
        items: [],
        current: 0,
        init: function() {
            var gallery = document.querySelectorAll('.imovel-galeria-item[data-full]');
            this.items = [];
            for (var i = 0; i < gallery.length; i++) {
                this.items.push(gallery[i].getAttribute('data-full'));
            }
        },
        open: function(el) {
            this.init();
            this.current = parseInt(el.getAttribute('data-index')) || 0;
            this.show();
            this.el.classList.add('active');
            document.body.style.overflow = 'hidden';
        },
        close: function() {
            this.el.classList.remove('active');
            document.body.style.overflow = '';
        },
        show: function() {
            if (this.items[this.current]) {
                this.img.style.backgroundImage = 'url(' + this.items[this.current] + ')';
                this.counter.textContent = (this.current + 1) + ' / ' + this.items.length;
            }
        },
        next: function() {
            this.current = (this.current + 1) % this.items.length;
            this.show();
        },
        prev: function() {
            this.current = (this.current - 1 + this.items.length) % this.items.length;
            this.show();
        }
    };

    // Fechar clicando no fundo
    lightbox.el.addEventListener('click', function(e) {
        if (e.target === lightbox.el) lightbox.close();
    });

    // Keyboard nav
    document.addEventListener('keydown', function(e) {
        if (!lightbox.el.classList.contains('active')) return;
        if (e.key === 'Escape') lightbox.close();
        if (e.key === 'ArrowRight') lightbox.next();
        if (e.key === 'ArrowLeft') lightbox.prev();
    });

    // Stop propagation on nav buttons
    var navBtns = lightbox.el.querySelectorAll('.imovel-lightbox-nav, .imovel-lightbox-close');
    for (var i = 0; i < navBtns.length; i++) {
        navBtns[i].addEventListener('click', function(e) { e.stopPropagation(); });
    }

    window.imovelLightbox = lightbox;
})();
</script>

<?php endwhile; ?>

<?php get_footer(); ?>
