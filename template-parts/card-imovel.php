<?php
// template-parts/card-imovel.php
$categoria = get_post_meta(get_the_ID(), '_imovel_categoria', true);
$preco     = get_post_meta(get_the_ID(), '_imovel_preco', true);
$bairro    = get_post_meta(get_the_ID(), '_imovel_bairro', true);
$tipo      = get_post_meta(get_the_ID(), '_imovel_tipo', true);
$quartos   = get_post_meta(get_the_ID(), '_imovel_quartos', true);
$banheiros = get_post_meta(get_the_ID(), '_imovel_banheiros', true);
$vagas     = get_post_meta(get_the_ID(), '_imovel_vagas', true);

$badges = [
  'lancamento'     => 'Lançamento',
  'pronto'         => 'Pronto p/ Morar',
  'ultimas'        => 'Últimas Unidades',
  'revenda'        => 'Revenda',
];
$badge = $badges[$categoria] ?? 'Destaque';
?>
<div class="mr-imovel-card">
  <div class="mr-imovel-img">
    <?php if (has_post_thumbnail()) : ?>
      <?php the_post_thumbnail('large'); ?>
    <?php else : ?>
      <div class="mr-imovel-img-placeholder">MR</div>
    <?php endif; ?>
    <div class="mr-imovel-badge"><?php echo esc_html($badge); ?></div>
  </div>

  <div class="mr-imovel-info">
    <div class="mr-imovel-tipo"><?php echo esc_html($tipo ?: 'Residencial'); ?></div>
    <div class="mr-imovel-nome"><?php the_title(); ?></div>
    <div class="mr-imovel-local">📍 <?php echo esc_html($bairro ?: 'Anápolis/GO'); ?></div>
  </div>

  <div class="mr-imovel-rodape">
    <div class="mr-imovel-preco">
      <?php if ($preco) : ?>
        R$ <?php echo esc_html(number_format((float)$preco, 0, ',', '.')); ?>
        <span>a partir de</span>
      <?php else : ?>
        Consulte <span>valor</span>
      <?php endif; ?>
    </div>

    <div style="display:flex;gap:12px;align-items:center;">
      <?php if ($quartos) : ?>
      <div class="mr-detalhe">
        <div style="font-size:.8rem;font-weight:600;color:var(--azul)"><?php echo esc_html($quartos); ?></div>
        <div style="font-size:.5rem;letter-spacing:1px;color:rgba(26,39,68,.4);text-transform:uppercase">Qtos</div>
      </div>
      <?php endif; ?>
      <?php if ($vagas) : ?>
      <div class="mr-detalhe">
        <div style="font-size:.8rem;font-weight:600;color:var(--azul)"><?php echo esc_html($vagas); ?></div>
        <div style="font-size:.5rem;letter-spacing:1px;color:rgba(26,39,68,.4);text-transform:uppercase">Vagas</div>
      </div>
      <?php endif; ?>
      <a href="https://wa.me/5562981148448?text=<?php echo urlencode('Olá Marcos Rosa! Vi o imóvel "' . get_the_title() . '" no site e gostaria de mais informações.'); ?>"
         class="mr-btn-card" target="_blank">Consultar</a>
    </div>
  </div>
</div>
