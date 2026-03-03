<!-- FOOTER -->
<footer class="mr-footer">
  <div class="mr-footer-grid">

    <div class="mr-footer-brand">
      <img src="<?php echo get_template_directory_uri(); ?>/assets/img/logo.png"
           alt="Marcos Rosa" class="mr-footer-logo">
      <p class="mr-footer-desc">
        Especialista em lançamentos e revendas em Anápolis/GO.
        Atendimento personalizado com foco no seu resultado.
      </p>
      <span class="mr-footer-creci">CRECI-GO 35088-F</span>
    </div>

    <div>
      <div class="mr-footer-titulo">Imóveis</div>
      <ul class="mr-footer-links">
        <li><a href="<?php echo home_url('/lancamentos'); ?>">Lançamentos</a></li>
        <li><a href="<?php echo home_url('/revendas'); ?>">Revendas</a></li>
        <li><a href="<?php echo home_url('/apartamentos'); ?>">Apartamentos</a></li>
        <li><a href="<?php echo home_url('/casas'); ?>">Casas</a></li>
        <li><a href="<?php echo home_url('/terrenos'); ?>">Terrenos</a></li>
      </ul>
    </div>

    <div>
      <div class="mr-footer-titulo">Links</div>
      <ul class="mr-footer-links">
        <li><a href="<?php echo home_url('/'); ?>">Início</a></li>
        <li><a href="<?php echo home_url('/#sobre'); ?>">Sobre Marcos Rosa</a></li>
        <li><a href="<?php echo home_url('/#vender'); ?>">Venda Conosco</a></li>
        <li><a href="<?php echo home_url('/#contato'); ?>">Contato</a></li>
      </ul>
    </div>

    <div>
      <div class="mr-footer-titulo">Contato</div>
      <ul class="mr-footer-links">
        <li><a href="https://wa.me/5562981148448">📱 (62) 98114-8448</a></li>
        <li><a href="mailto:mrcimoveis78@gmail.com">✉️ mrcimoveis78@gmail.com</a></li>
        <li><span>📍 Anápolis/GO</span></li>
        <li><a href="https://instagram.com" target="_blank">📸 Instagram</a></li>
      </ul>
    </div>

  </div>

  <div class="mr-linha-decorativa"></div>

  <div class="mr-footer-bottom">
    <div class="mr-footer-copy">
      © <?php echo date('Y'); ?> Marcos Rosa · CRECI-GO 35088-F · Todos os direitos reservados
    </div>
    <div class="mr-footer-social">
      <a href="https://instagram.com" class="mr-social-btn" target="_blank">ig</a>
      <a href="https://facebook.com" class="mr-social-btn" target="_blank">fb</a>
      <a href="https://youtube.com" class="mr-social-btn" target="_blank">yt</a>
    </div>
  </div>
</footer>

<!-- WhatsApp Flutuante -->
<a href="https://wa.me/5562981148448" class="mr-wpp-float" target="_blank" title="Falar com Marcos Rosa">
  💬
</a>

<?php wp_footer(); ?>
</body>
</html>
