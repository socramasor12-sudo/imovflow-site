/**
 * Marcos Rosa — main.js v2.1.0
 * Formulário → WhatsApp direto (sem depender de AJAX)
 */
document.addEventListener('DOMContentLoaded', function() {

  // ─── MENU MOBILE ─────────────────────────────────
  var menuToggle = document.querySelector('.menu-toggle');
  var navMenu    = document.querySelector('.nav-menu');
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      menuToggle.classList.toggle('active');
    });
    navMenu.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        navMenu.classList.remove('active');
        menuToggle.classList.remove('active');
      });
    });
  }

  // ─── SMOOTH SCROLL ───────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── FORMULÁRIO CAPTAÇÃ� -> WHATSAPP DIRETO ───────────
  var form = document.getElementById('form-captacao');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      var nome    = (form.querySelector('[name="nome"]') || {}).value || '';
      var wpp     = (form.querySelector('[name="whatsapp"]') || {}).value || '';
      var tipo    = (form.querySelector('[name="tipo"]') || {}).value || '';
      var bairro  = (form.querySelector('[name="bairro"]') || {}).value || '';
      var valor   = (form.querySelector('[name="valor"]') || {}).value || '';

      if (!nome || !wpp) {
        alert('Por favor, preencha seu nome e WhatsApp.');
        return;
      }

      var msg = 'Olá Marcos! Me chamo ' + nome + ' e tenho um imóvel para anunciar.'
              + '\n\nTipo: ' + (tipo || 'Não informado')
              + '\nBairro: ' + (bairro || 'Não informado')
              + '\nValor pretendido: R$ ' + (valor || 'Não informado')
              + '\nMeu WhatsApp: ' + wpp
              + '\n\nEnviado pelo site imovflow.com.br';

      var url = 'https://api.whatsapp.com/send?phone=5562981148448&text=' + encodeURIComponent(msg);
      window.open(url, '_blank');

      var msgDiv = document.getElementById('captacao-msg') || document.querySelector('.mr-captacao-msg');
      if (msgDiv) {
        msgDiv.style.display = 'block';
        msgDiv.className = 'mr-captacao-msg-ok';
        msgDiv.textContent = 'Redirecionando para o WhatsApp...';
        setTimeout(function() { msgDiv.style.display = 'none'; }, 5000);
      }

      if (typeof marcosRosa !== 'undefined' && marcosRosa.ajaxurl) {
        var fd = new FormData(form);
        fd.append('action', 'marcos_rosa_captacao');
        fd.append('nonce', marcosRosa.nonce);
        fetch(marcosRosa.ajaxurl, { method: 'POST', body: fd }).catch(function() {});
      }

      form.reset();
    });
  }

  // ─── OCULTAR WPP FLOAT PERTO DO FOOTER ───────────
  (function() {
    var float  = document.querySelector('.mr-wpp-float');
    var footer = document.querySelector('.mr-footer');
    if (!float || !footer) return;
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        float.style.opacity       = e.isIntersecting ? '0' : '1';
        float.style.pointerEvents = e.isIntersecting ? 'none' : 'auto';
      });
    }, { threshold: 0.1 });
    observer.observe(footer);
  })();

}); // end DOMContentLoaded