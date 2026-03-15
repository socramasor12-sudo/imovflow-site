<?php
// template-parts/card-imovel.php
$id         = get_the_ID();
$tipo       = get_post_meta($id, '_imovel_tipo', true);
$finalidade = get_post_meta($id, '_imovel_finalidade', true);
$valor      = get_post_meta($id, '_imovel_valor', true);
$area       = get_post_meta($id, '_imovel_area', true);
$quartos    = get_post_meta($id, '_imovel_quartos', true);
$banheiros  = get_post_meta($id, '_imovel_banheiros', true);
$vagas      = get_post_meta($id, '_imovel_vagas', true);
$bairro     = get_post_meta($id, '_imovel_bairro', true);
$badge      = get_post_meta($id, '_imovel_badge', true);

// Format valor
if ($valor !== '' && is_numeric(str_replace(['.', ','], '', $valor))) {
    $valor_numerico = (float) str_replace(['.', ','], ['', '.'], $valor);
    // If value looks like it uses dot as thousands separator (e.g. "350.000"), parse accordingly
    if (preg_match('/^\d{1,3}(\.\d{3})+$/', trim($valor))) {
        $valor_numerico = (float) str_replace('.', '', $valor);
    }
    $preco_formatado = 'R$ ' . number_format($valor_numerico, 0, ',', '.');
} elseif ($valor !== '') {
    $preco_formatado = 'R$ ' . esc_html($valor);
} else {
    $preco_formatado = null;
}
?>
<a class="imovel-card" href="<?php echo esc_url(get_permalink()); ?>">

  <div class="imovel-img">
    <?php if (has_post_thumbnail()) : ?>
      <?php the_post_thumbnail('medium', ['class' => 'imovel-thumb']); ?>
    <?php else : ?>
      <div class="imovel-img-placeholder">MR</div>
    <?php endif; ?>
    <?php if ($badge) : ?>
      <div class="imovel-badge"><?php echo esc_html($badge); ?></div>
    <?php endif; ?>
  </div>

  <div class="imovel-info">
    <?php if ($tipo) : ?>
      <div class="imovel-tipo"><?php echo esc_html($tipo); ?></div>
    <?php endif; ?>
    <div class="imovel-nome"><?php the_title(); ?></div>
    <?php if ($bairro) : ?>
      <div class="imovel-local">📍 <?php echo esc_html($bairro); ?></div>
    <?php endif; ?>
  </div>

  <div class="imovel-rodape">
    <div class="imovel-preco">
      <?php if ($preco_formatado) : ?>
        <?php echo $preco_formatado; ?>
        <?php if ($finalidade) : ?>
          <small class="imovel-finalidade"><?php echo esc_html($finalidade); ?></small>
        <?php endif; ?>
      <?php else : ?>
        Consulte o valor
      <?php endif; ?>
    </div>

    <?php $tem_detalhes = $quartos || $banheiros || $vagas || $area; ?>
    <?php if ($tem_detalhes) : ?>
    <div class="imovel-detalhes">
      <?php if ($quartos) : ?>
      <div class="detalhe">
        <span class="detalhe-num"><?php echo esc_html($quartos); ?></span>
        <span class="detalhe-label">Qtos</span>
      </div>
      <?php endif; ?>
      <?php if ($banheiros) : ?>
      <div class="detalhe">
        <span class="detalhe-num"><?php echo esc_html($banheiros); ?></span>
        <span class="detalhe-label">Banheiros</span>
      </div>
      <?php endif; ?>
      <?php if ($vagas) : ?>
      <div class="detalhe">
        <span class="detalhe-num"><?php echo esc_html($vagas); ?></span>
        <span class="detalhe-label">Vagas</span>
      </div>
      <?php endif; ?>
      <?php if ($area) : ?>
      <div class="detalhe">
        <span class="detalhe-num"><?php echo esc_html($area); ?></span>
        <span class="detalhe-label">m²</span>
      </div>
      <?php endif; ?>
    </div>
    <?php endif; ?>
  </div>

</a>
