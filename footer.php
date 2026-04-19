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
        <li><a href="mailto:<?php echo antispambot('mrcimoveis78@gmail.com'); ?>">✉️ <?php echo antispambot('mrcimoveis78@gmail.com'); ?></a></li>
        <li><span>📍 Anápolis/GO</span></li>
      </ul>
    </div>

  </div>

  <div class="mr-linha-decorativa"></div>

  <div class="mr-footer-bottom">
    <div class="mr-footer-copy">
      © <?php echo date('Y'); ?> Marcos Rosa · CRECI-GO 35088-F · Todos os direitos reservados
    </div>
    <div class="mr-footer-social">
      <a href="https://instagram.com/marcosrosa.corretor" target="_blank" title="Instagram" class="mr-social-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
      </a>
      <a href="https://facebook.com/marcosrosa.corretor" target="_blank" title="Facebook" class="mr-social-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
      </a>
      <a href="https://youtube.com/@marcosrosa" target="_blank" title="YouTube" class="mr-social-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46a2.78 2.78 0 0 0-1.95 1.96A29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.41 19.6C5.12 20 12 20 12 20s6.88 0 8.59-.46a2.78 2.78 0 0 0 1.95-1.95A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="currentColor" stroke="none"/></svg>
      </a>
    </div>
  </div>
</footer>

<!-- WhatsApp flutuante removido: coberto pelo JoinChat -->


<script>
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-captacao');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = form.querySelector('button');
            const msg = document.getElementById('form-message');
            const originalBtnText = btn.innerHTML;
            
            btn.innerHTML = '⌛ Enviando...';
            btn.disabled = true;
            
            const formData = new FormData(form);
            formData.append('action', 'marcos_rosa_captacao');
            formData.append('nonce', '<?php echo wp_create_nonce("marcos_rosa_nonce"); ?>');
            
            fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    msg.style.color = '#c9a84c';
                    msg.innerHTML = '✅ Recebido! Marcos Rosa entrará em contato em breve.';
                    msg.style.display = 'block';
                    form.reset();
                } else {
                    msg.style.color = '#ff4444';
                    msg.innerHTML = '❌ Ocorreu um erro. Tente novamente ou chame no WhatsApp.';
                    msg.style.display = 'block';
                }
            })
            .catch(error => {
                msg.style.color = '#ff4444';
                msg.innerHTML = '❌ Erro de conexão. Tente o WhatsApp.';
                msg.style.display = 'block';
            })
            .finally(() => {
                btn.innerHTML = originalBtnText;
                btn.disabled = false;
            });
        });
    }
});
</script>

<?php wp_footer(); ?>
</body>
</html>
