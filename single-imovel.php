<?php
/**
 * Template para exibição individual de imóvel (CPT: imovel)
 * Marcos Rosa Corretor — CRECI-GO 35088-F
 */
get_header();
?>

<?php while (have_posts()) : the_post();
    $tipo       = get_post_meta(get_the_ID(), '_imovel_tipo',       true);
    $finalidade = get_post_meta(get_the_ID(), '_imovel_finalidade', true);
    $valor      = get_post_meta(get_the_ID(), '_imovel_valor',      true);
    $area       = get_post_meta(get_the_ID(), '_imovel_area',       true);
    $quartos    = get_post_meta(get_the_ID(), '_imovel_quartos',    true);
    $banheiros  = get_post_meta(get_the_ID(), '_imovel_banheiros',  true);
    $vagas      = get_post_meta(get_the_ID(), '_imovel_vagas',      true);
    $bairro     = get_post_meta(get_the_ID(), '_imovel_bairro',     true);
    $badge      = get_post_meta(get_the_ID(), '_imovel_badge',      true);

    // Formata valor: "350000" → "R$ 350.000"
    $valor_fmt = '';
    if ($valor) {
        $valor_fmt = 'R$ ' . number_format((float) $valor, 0, ',', '.');
    }

    // Link WhatsApp com texto pré-preenchido
    $wpp_texto = 'Tenho interesse neste imóvel: ' . get_the_title();
    $wpp_link  = 'https://wa.me/5562981148448?text=' . rawurlencode($wpp_texto);
?>

<!-- ─── HERO DO IMÓVEL ──────────────────────────────────────────────── -->
<section style="
    background: var(--azul);
    padding: 140px 60px 60px;
    text-align: center;
    border-bottom: 1px solid rgba(201,168,76,0.2);
">
    <?php if ($badge) : ?>
        <div class="imovel-badge" style="
            position: static;
            display: inline-block;
            margin-bottom: 20px;
            font-size: 0.55rem;
            letter-spacing: 3px;
        "><?php echo esc_html($badge); ?></div>
    <?php endif; ?>

    <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
        <?php if ($tipo) : ?>
            <span class="imovel-tipo" style="
                background: rgba(201,168,76,0.15);
                border: 1px solid rgba(201,168,76,0.3);
                padding: 6px 16px;
                border-radius: 2px;
                font-size: 0.55rem;
                letter-spacing: 3px;
                color: var(--dourado);
                text-transform: uppercase;
            "><?php echo esc_html($tipo); ?></span>
        <?php endif; ?>
        <?php if ($finalidade) : ?>
            <span style="
                background: rgba(201,168,76,0.1);
                border: 1px solid rgba(201,168,76,0.2);
                padding: 6px 16px;
                border-radius: 2px;
                font-size: 0.55rem;
                letter-spacing: 3px;
                color: rgba(248,246,241,0.7);
                text-transform: uppercase;
            "><?php echo esc_html($finalidade); ?></span>
        <?php endif; ?>
    </div>

    <h1 style="
        font-family: 'Cormorant Garamond', serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 300;
        color: var(--branco);
        line-height: 1.15;
        margin-bottom: 16px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    "><?php the_title(); ?></h1>

    <?php if ($bairro) : ?>
        <div style="
            font-size: 0.7rem;
            letter-spacing: 2px;
            color: rgba(248,246,241,0.5);
            text-transform: uppercase;
        ">📍 <?php echo esc_html($bairro); ?>, Anápolis/GO</div>
    <?php endif; ?>
</section>

<!-- ─── LAYOUT PRINCIPAL (imagem + detalhes) ────────────────────────── -->
<section style="
    background: var(--branco);
    padding: 60px;
">
    <div style="
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 48px;
        align-items: start;
    " class="single-imovel-grid">

        <!-- IMAGEM PRINCIPAL -->
        <div style="position: relative; overflow: hidden; border-radius: 2px; background: var(--cinza-claro);">
            <?php if (has_post_thumbnail()) : ?>
                <?php the_post_thumbnail('large', [
                    'style' => 'width:100%; height:auto; display:block; object-fit:cover;',
                    'alt'   => esc_attr(get_the_title()),
                ]); ?>
            <?php else : ?>
                <div class="imovel-img-placeholder" style="
                    height: 400px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, var(--azul) 0%, var(--azul-medio) 100%);
                    font-family: 'Cormorant Garamond', serif;
                    font-size: 5rem;
                    color: rgba(201,168,76,0.25);
                    letter-spacing: 8px;
                ">MR</div>
            <?php endif; ?>
        </div>

        <!-- CARD DE DETALHES -->
        <div style="
            background: white;
            border: 1px solid var(--cinza-claro);
            padding: 40px;
            display: flex;
            flex-direction: column;
            gap: 0;
        ">
            <!-- Valor -->
            <?php if ($valor_fmt) : ?>
                <div style="
                    padding-bottom: 28px;
                    border-bottom: 1px solid var(--cinza-claro);
                    margin-bottom: 28px;
                ">
                    <div style="
                        font-size: 0.55rem;
                        letter-spacing: 3px;
                        color: var(--dourado-escuro);
                        text-transform: uppercase;
                        margin-bottom: 8px;
                    ">Valor</div>
                    <div class="imovel-preco" style="font-size: 2.2rem;">
                        <?php echo esc_html($valor_fmt); ?>
                    </div>
                </div>
            <?php endif; ?>

            <!-- Características numéricas -->
            <?php if ($area || $quartos || $banheiros || $vagas) : ?>
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
                    gap: 16px;
                    padding-bottom: 28px;
                    border-bottom: 1px solid var(--cinza-claro);
                    margin-bottom: 28px;
                ">
                    <?php if ($area) : ?>
                        <div class="detalhe" style="padding: 16px; background: var(--cinza-claro);">
                            <div class="detalhe-num" style="font-size: 1.1rem;"><?php echo esc_html($area); ?></div>
                            <div class="detalhe-label">m²</div>
                        </div>
                    <?php endif; ?>
                    <?php if ($quartos) : ?>
                        <div class="detalhe" style="padding: 16px; background: var(--cinza-claro);">
                            <div class="detalhe-num" style="font-size: 1.1rem;"><?php echo absint($quartos); ?></div>
                            <div class="detalhe-label">Quartos</div>
                        </div>
                    <?php endif; ?>
                    <?php if ($banheiros) : ?>
                        <div class="detalhe" style="padding: 16px; background: var(--cinza-claro);">
                            <div class="detalhe-num" style="font-size: 1.1rem;"><?php echo absint($banheiros); ?></div>
                            <div class="detalhe-label">Banheiros</div>
                        </div>
                    <?php endif; ?>
                    <?php if ($vagas) : ?>
                        <div class="detalhe" style="padding: 16px; background: var(--cinza-claro);">
                            <div class="detalhe-num" style="font-size: 1.1rem;"><?php echo absint($vagas); ?></div>
                            <div class="detalhe-label">Vagas</div>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <!-- Dados complementares -->
            <?php if ($tipo || $finalidade || $bairro) : ?>
                <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 32px;">
                    <?php if ($tipo) : ?>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; letter-spacing: 1px;">
                            <span style="color: rgba(26,39,68,0.45); text-transform: uppercase; letter-spacing: 2px; font-size: 0.55rem;">Tipo</span>
                            <span style="color: var(--azul); font-weight: 600;"><?php echo esc_html($tipo); ?></span>
                        </div>
                    <?php endif; ?>
                    <?php if ($finalidade) : ?>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; letter-spacing: 1px;">
                            <span style="color: rgba(26,39,68,0.45); text-transform: uppercase; letter-spacing: 2px; font-size: 0.55rem;">Finalidade</span>
                            <span style="color: var(--azul); font-weight: 600;"><?php echo esc_html($finalidade); ?></span>
                        </div>
                    <?php endif; ?>
                    <?php if ($bairro) : ?>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; letter-spacing: 1px;">
                            <span style="color: rgba(26,39,68,0.45); text-transform: uppercase; letter-spacing: 2px; font-size: 0.55rem;">Bairro</span>
                            <span style="color: var(--azul); font-weight: 600;"><?php echo esc_html($bairro); ?></span>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <!-- Botão WhatsApp CTA -->
            <a href="<?php echo esc_url($wpp_link); ?>"
               target="_blank"
               rel="noopener noreferrer"
               class="btn-primary"
               style="
                   justify-content: center;
                   padding: 18px 28px;
                   font-size: 0.65rem;
                   letter-spacing: 2px;
                   background: var(--dourado);
                   color: var(--azul);
                   text-align: center;
               ">
                💬 Tenho interesse neste imóvel
            </a>
        </div>
    </div>
</section>

<!-- ─── DESCRIÇÃO COMPLETA ───────────────────────────────────────────── -->
<?php if (get_the_content()) : ?>
<section style="
    background: white;
    border-top: 1px solid var(--cinza-claro);
    padding: 60px;
">
    <div style="max-width: 800px; margin: 0 auto;">
        <div style="
            font-size: 0.55rem;
            letter-spacing: 4px;
            color: var(--dourado-escuro);
            text-transform: uppercase;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="display:inline-block; width:30px; height:1px; background:var(--dourado);"></span>
            Descrição
        </div>
        <h2 style="
            font-family: 'Cormorant Garamond', serif;
            font-size: 2rem;
            font-weight: 300;
            color: var(--azul);
            margin-bottom: 32px;
        ">Sobre este imóvel</h2>

        <div style="
            font-size: 0.8rem;
            font-weight: 300;
            letter-spacing: 1px;
            line-height: 2;
            color: rgba(26,39,68,0.75);
        " class="entry-content">
            <?php the_content(); ?>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- ─── CTA WHATSAPP FINAL ───────────────────────────────────────────── -->
<section style="
    background: var(--azul);
    padding: 80px 60px;
    text-align: center;
    border-top: 1px solid rgba(201,168,76,0.2);
">
    <div style="max-width: 600px; margin: 0 auto;">
        <div class="section-tag" style="
            justify-content: center;
            margin-bottom: 16px;
            color: rgba(201,168,76,0.7);
        ">Pronto para dar o próximo passo?</div>
        <h2 style="
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(1.8rem, 4vw, 2.8rem);
            font-weight: 300;
            color: var(--branco);
            margin-bottom: 12px;
            line-height: 1.2;
        ">Fale com <span style="color:var(--dourado); font-style:italic;">Marcos Rosa</span></h2>
        <p style="
            font-size: 0.7rem;
            font-weight: 300;
            letter-spacing: 1.5px;
            color: rgba(248,246,241,0.55);
            margin-bottom: 40px;
            line-height: 2;
        ">Corretor de Imóveis · CRECI-GO 35088-F · Atendimento 7 dias por semana</p>

        <a href="<?php echo esc_url($wpp_link); ?>"
           target="_blank"
           rel="noopener noreferrer"
           class="btn-primary"
           style="
               display: inline-flex;
               padding: 18px 48px;
               font-size: 0.65rem;
               letter-spacing: 3px;
               background: var(--dourado);
               color: var(--azul);
           ">
            💬 Tenho interesse neste imóvel
        </a>
    </div>
</section>

<!-- ─── RESPONSIVIDADE (mobile) ─────────────────────────────────────── -->
<style>
@media (max-width: 768px) {
    .single-imovel-grid {
        grid-template-columns: 1fr !important;
    }
    section {
        padding-left: 24px !important;
        padding-right: 24px !important;
    }
}
</style>

<?php endwhile; ?>

<?php get_footer(); ?>
