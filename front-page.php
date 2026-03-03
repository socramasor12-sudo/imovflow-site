<?php get_header(); ?>

<!-- HERO -->
<section class="hero" id="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <p class="hero-eyebrow">Corretor Imobiliário · CRECI-GO 35088-F</p>
        <h1 class="hero-title">Seu imóvel ideal<br>em Anápolis</h1>
        <p class="hero-subtitle">Especialista em lançamentos e revendas na região de Anápolis&nbsp;– GO</p>
        <a href="#imoveis" class="btn btn-primary">Ver Imóveis</a>

        <div class="hero-stats">
            <div class="stat">
                <span class="stat-number">4+</span>
                <span class="stat-label">Anos de experiência</span>
            </div>
            <div class="stat">
                <span class="stat-number">30+</span>
                <span class="stat-label">Empreendimentos</span>
            </div>
        </div>
    </div>
</section>

<!-- BUSCA -->
<section class="busca-section" id="busca">
    <div class="container">
        <form class="busca-form" onsubmit="buscar(event)">
            <div class="busca-field">
                <label for="finalidade">Finalidade</label>
                <select id="finalidade" name="finalidade">
                    <option value="">Todos</option>
                    <option value="comprar">Comprar</option>
                    <option value="alugar">Alugar</option>
                </select>
            </div>
            <div class="busca-field">
                <label for="tipo">Tipo</label>
                <select id="tipo" name="tipo">
                    <option value="">Todos</option>
                    <option value="apartamento">Apartamento</option>
                    <option value="casa">Casa</option>
                    <option value="terreno">Terreno</option>
                    <option value="comercial">Comercial</option>
                </select>
            </div>
            <div class="busca-field">
                <label for="bairro">Bairro</label>
                <input type="text" id="bairro" name="bairro" placeholder="Ex: Jundiaí">
            </div>
            <button type="submit" class="btn btn-primary">Buscar</button>
        </form>
    </div>
</section>

<!-- LANÇAMENTOS -->
<section class="lancamentos-section" id="imoveis">
    <div class="container">
        <h2 class="section-title">Lançamentos</h2>
        <p class="section-subtitle">Conheça os melhores empreendimentos disponíveis</p>

        <div class="imoveis-grid">
            <?php
            $query = new WP_Query( array(
                'post_type'      => 'imovel',
                'posts_per_page' => 9,
                'post_status'    => 'publish',
                'meta_query'     => array(
                    array(
                        'key'     => '_imovel_categoria',
                        'value'   => 'lancamento',
                        'compare' => '=',
                    ),
                ),
            ) );

            if ( $query->have_posts() ) :
                while ( $query->have_posts() ) :
                    $query->the_post();
                    get_template_part( 'template-parts/card-imovel' );
                endwhile;
                wp_reset_postdata();
            else :
            ?>
                <p class="no-results">Nenhum lançamento disponível no momento. Entre em contato para mais informações.</p>
            <?php endif; ?>
        </div>
    </div>
</section>

<!-- CAPTAÇÃO / VENDER -->
<section class="captacao-section" id="vender">
    <div class="container">
        <div class="captacao-inner">
            <div class="captacao-info">
                <h2 class="section-title">Quer vender seu imóvel?</h2>
                <p>Faça uma avaliação gratuita e conte com a expertise de quem conhece o mercado de Anápolis.</p>
                <ul class="captacao-beneficios">
                    <li>Avaliação gratuita e sem compromisso</li>
                    <li>Divulgação em múltiplas plataformas</li>
                    <li>Acompanhamento personalizado</li>
                    <li>Documentação e negociação segura</li>
                </ul>
            </div>

            <form class="captacao-form" id="captacao-form">
                <?php wp_nonce_field( 'captacao_nonce', 'captacao_nonce_field' ); ?>

                <div class="form-group">
                    <label for="cap-nome">Nome *</label>
                    <input type="text" id="cap-nome" name="nome" required placeholder="Seu nome completo">
                </div>
                <div class="form-group">
                    <label for="cap-telefone">Telefone *</label>
                    <input type="tel" id="cap-telefone" name="telefone" required placeholder="(62) 9 0000-0000">
                </div>
                <div class="form-group">
                    <label for="cap-email">E-mail</label>
                    <input type="email" id="cap-email" name="email" placeholder="seuemail@exemplo.com">
                </div>
                <div class="form-group">
                    <label for="cap-endereco">Endereço do imóvel</label>
                    <input type="text" id="cap-endereco" name="endereco" placeholder="Rua, número, bairro">
                </div>
                <div class="form-group">
                    <label for="cap-tipo">Tipo do imóvel</label>
                    <select id="cap-tipo" name="tipo">
                        <option value="">Selecione</option>
                        <option value="apartamento">Apartamento</option>
                        <option value="casa">Casa</option>
                        <option value="terreno">Terreno</option>
                        <option value="comercial">Comercial</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="cap-mensagem">Informações adicionais</label>
                    <textarea id="cap-mensagem" name="mensagem" rows="4" placeholder="Área, características, valor esperado..."></textarea>
                </div>

                <button type="submit" class="btn btn-primary btn-full">Solicitar Avaliação Gratuita</button>
                <div class="form-feedback" id="captacao-feedback" aria-live="polite"></div>
            </form>
        </div>
    </div>
</section>

<!-- SOBRE -->
<section class="sobre-section" id="sobre">
    <div class="container">
        <div class="sobre-inner">
            <div class="sobre-photo">
                <img
                    src="<?php echo esc_url( get_template_directory_uri() . '/assets/img/marcos-rosa.jpg' ); ?>"
                    alt="Marcos Rosa - Corretor Imobiliário"
                    loading="lazy"
                >
            </div>
            <div class="sobre-content">
                <h2 class="section-title">Sobre Marcos Rosa</h2>
                <p class="sobre-creci">CRECI-GO 35088-F</p>
                <p>Com mais de 4 anos de experiência no mercado imobiliário de Anápolis, Marcos Rosa é especialista em lançamentos e revendas, oferecendo atendimento personalizado e transparente para cada cliente.</p>
                <p>Mais de 30 empreendimentos comercializados com sucesso, sempre priorizando a satisfação e a segurança nas transações imobiliárias.</p>
                <a
                    href="https://wa.me/5562981148448"
                    class="btn btn-primary"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Fale Comigo
                </a>
            </div>
        </div>
    </div>
</section>

<!-- CTA -->
<section class="cta-section" id="contato">
    <div class="container">
        <h2>Pronto para encontrar seu imóvel ideal?</h2>
        <p>Entre em contato agora e dê o primeiro passo rumo ao imóvel dos seus sonhos.</p>
        <div class="cta-buttons">
            <a
                href="https://wa.me/5562981148448"
                class="btn btn-whatsapp-cta"
                target="_blank"
                rel="noopener noreferrer"
            >
                Chamar no WhatsApp
            </a>
            <a href="tel:+5562981148448" class="btn btn-outline">Ligar agora</a>
        </div>
    </div>
</section>

<?php get_footer(); ?>
