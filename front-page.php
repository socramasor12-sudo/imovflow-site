<?php get_header(); ?>

<!-- HERO -->
<section class="hero">
  <div class="hero-esquerda">
    <div class="hero-tag">Corretor de Imóveis em Anápolis/GO</div>
    <h1 class="hero-titulo">Seu imóvel<br>ideal em <span>Anápolis</span></h1>
    <p class="hero-subtitulo">Lançamentos e Revendas exclusivas</p>
    <div class="hero-linha"></div>
    <p class="hero-desc">
      Especialista em lançamentos residenciais e oportunidades de revenda em Anápolis/GO. 
      Atendimento personalizado, transparência e resultado em cada negociação.
    </p>
    <div class="hero-btns">
      <a href="#imoveis" class="btn-primary">🏠 Ver Imóveis</a>
      <a href="#sobre" class="btn-secondary">Conhecer Marcos Rosa</a>
    </div>
  </div>
  <div class="hero-direita">
    <div class="hero-img-bg">
      <img src="<?php echo get_template_directory_uri(); ?>/assets/img/logo.png" class="hero-logo-grande" alt="">
    </div>
    <div class="hero-overlay"></div>
  </div>
  <div class="hero-stats">
    <div class="stat"><div class="stat-numero">5+</div><div class="stat-label">Anos de experiência</div></div>
    <div class="stat"><div class="stat-numero">100+</div><div class="stat-label">Negócios realizados</div></div>
    <div class="stat"><div class="stat-numero">30+</div><div class="stat-label">Empreendimentos</div></div>
  </div>
</section>

<!-- BUSCA -->
<section class="busca-section">
  <div class="busca-container">
    <div class="busca-titulo">Encontre seu Imóvel</div>
    <div class="busca-form">
      <div class="busca-campo">
        <label>Finalidade</label>
        <select><option>Comprar</option><option>Lançamento</option><option>Revenda</option></select>
      </div>
      <div class="busca-campo">
        <label>Tipo</label>
        <select><option>Apartamento</option><option>Casa</option><option>Terreno</option><option>Comercial</option></select>
      </div>
      <div class="busca-campo">
        <label>Bairro / Região</label>
        <input type="text" placeholder="Ex: Jundiaí, Maracanã...">
      </div>
      <button class="btn-busca">Buscar →</button>
    </div>
  </div>
</section>

<!-- LANÇAMENTOS -->
<?php
$imoveis = new WP_Query([
    'post_type'      => 'imovel',
    'posts_per_page' => 6,
    'post_status'    => 'publish',
]);
if ($imoveis->have_posts()) : ?>
<section class="imoveis-section" id="imoveis">
  <div class="section-header">
    <div>
      <div class="section-tag">Novidades</div>
      <h2 class="section-titulo">Lançamentos em<br><span>Anápolis/GO</span></h2>
    </div>
    <a href="<?php echo esc_url(get_post_type_archive_link('imovel')); ?>" class="ver-todos">Ver todos</a>
  </div>
  <div class="imoveis-grid">
    <?php while ($imoveis->have_posts()) : $imoveis->the_post(); ?>
        <?php get_template_part('template-parts/card-imovel'); ?>
    <?php endwhile; wp_reset_postdata(); ?>
  </div>
</section>
<?php endif; ?>

<!-- SOBRE -->
<section class="sobre-section" id="sobre">

  <div class="sobre-foto">
    <img src="<?php echo esc_url(get_template_directory_uri()); ?>/assets/img/marcos-rosa.png"
         alt="Marcos Rosa — Corretor de Imóveis CRECI-GO 35088-F"
         style="width:100%;height:600px;object-fit:cover;object-position:center 20%;display:block;max-width:none;max-height:none;">
  </div>

  <div class="sobre-conteudo">
    <div class="section-tag" style="color:rgba(201,168,76,0.6)">Conheça</div>
    <h2 class="sobre-titulo">Marcos <span>Rosa</span></h2>
    <div class="sobre-subtitulo">Corretor de Imóveis · CRECI-GO 35088-F</div>
    <p class="sobre-texto">
      "Meu compromisso vai além da venda. É sobre encontrar o lugar certo 
      para cada família, o investimento ideal para cada objetivo. 
      Em Anápolis, conheço cada oportunidade do mercado."
    </p>
    <div class="sobre-valores">
      <div class="valor-item"><div class="valor-icone">🏆</div><div><div class="valor-nome">Experiência</div><div class="valor-desc">Anos atuando no mercado imobiliário de Anápolis/GO</div></div></div>
      <div class="valor-item"><div class="valor-icone">🤝</div><div><div class="valor-nome">Transparência</div><div class="valor-desc">Negociação clara e honesta em cada etapa</div></div></div>
      <div class="valor-item"><div class="valor-icone">📍</div><div><div class="valor-nome">Especialista Local</div><div class="valor-desc">Profundo conhecimento do mercado de Anápolis</div></div></div>
      <div class="valor-item"><div class="valor-icone">⚡</div><div><div class="valor-nome">Agilidade</div><div class="valor-desc">Atendimento via WhatsApp 7 dias por semana</div></div></div>
    </div>
    <a href="https://wa.me/5562981148448" class="btn-primary">💬 Falar com Marcos Rosa</a>
  </div>
</section>


<!-- CAPTAÇÃO DE IMÓVEIS -->
<section class="captacao-section" id="vender">
  <div class="captacao-esquerda">
    <div class="section-tag">Para Proprietários</div>
    <h2 class="captacao-titulo">Quer vender ou<br>anunciar seu <span>imóvel?</span></h2>
    <p class="captacao-desc">
      Tenho uma carteira ativa de compradores em Anápolis/GO. 
      Seu imóvel na mão certa vende mais rápido e pelo melhor preço.
      Atendimento personalizado do anúncio ao fechamento.
    </p>
    <div class="captacao-beneficios">
      <div class="beneficio">
        <div class="beneficio-icone">📸</div>
        <div class="beneficio-texto">Fotos e divulgação profissional sem custo</div>
      </div>
      <div class="beneficio">
        <div class="beneficio-icone">🎯</div>
        <div class="beneficio-texto">Avaliação gratuita do seu imóvel</div>
      </div>
      <div class="beneficio">
        <div class="beneficio-icone">📲</div>
        <div class="beneficio-texto">Anúncio em múltiplos portais e redes sociais</div>
      </div>
      <div class="beneficio">
        <div class="beneficio-icone">🤝</div>
        <div class="beneficio-texto">Suporte completo até a assinatura do contrato</div>
      </div>
    </div>
  </div>

  <div class="captacao-direita">
    <div class="captacao-form-titulo">Cadastre seu Imóvel</div>
    <div class="captacao-form-sub">Retorno em até 24 horas</div>

    <form id="form-captacao" class="mr-form-captacao">
      <div class="form-campo">
        <label>Seu Nome</label>
        <input type="text" name="nome" required placeholder="Nome completo">
      </div>
      <div class="form-grid">
        <div class="form-campo">
          <label>WhatsApp</label>
          <input type="text" name="whatsapp" required placeholder="(62) 9 ....">
        </div>
        <div class="form-campo">
          <label>Tipo do Imóvel</label>
          <select name="tipo" required>
            <option value="">Selecione</option>
            <option>Apartamento</option>
            <option>Casa</option>
            <option>Terreno</option>
            <option>Comercial</option>
          </select>
        </div>
      </div>
      <div class="form-campo">
        <label>Bairro / Localização</label>
        <input type="text" name="localizacao" required placeholder="Ex: Jundiaí, Centro...">
      </div>
      <div class="form-campo">
        <label>Valor Pretendido (R$)</label>
        <input type="text" name="valor" placeholder="Ex: 350.000">
      </div>
      <button type="submit" class="btn-captacao">📲 Quero Anunciar Meu Imóvel</button>
      <div id="form-message" style="margin-top: 15px; font-size: 0.8rem; display: none;"></div>
    </form>
  </div>
</section>

<!-- CTA -->
<section class="cta-section">
  <div>
    <div class="cta-tag">Pronto para começar?</div>
    <div class="cta-titulo">Encontre seu imóvel<br><span>ideal hoje</span></div>
  </div>
</section>

<?php get_footer(); ?>