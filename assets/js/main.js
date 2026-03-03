// ═══════════════════════════════════════
// MARCOS ROSA — JS Principal
// CRECI-GO 35088-F
// ═══════════════════════════════════════

document.addEventListener('DOMContentLoaded', function () {

  // ─── HEADER SCROLL ───────────────────
  const header = document.getElementById('mr-header');
  window.addEventListener('scroll', () => {
    header?.classList.toggle('scrolled', window.scrollY > 50);
  });

  // ─── MENU MOBILE ─────────────────────
  const toggle = document.getElementById('mr-menu-toggle');
  const nav    = document.querySelector('.mr-nav');
  toggle?.addEventListener('click', () => {
    nav?.classList.toggle('open');
  });

  // ─── SMOOTH SCROLL PARA ÂNCORAS ──────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        nav?.classList.remove('open');
      }
    });
  });

});

// ─── BUSCA ─────────────────────────────
function executarBusca() {
  const finalidade = document.getElementById('busca-finalidade')?.value || '';
  const tipo       = document.getElementById('busca-tipo')?.value || '';
  const bairro     = document.getElementById('busca-bairro')?.value || '';

  const params = new URLSearchParams();
  if (finalidade) params.set('finalidade', finalidade);
  if (tipo)       params.set('tipo', tipo);
  if (bairro)     params.set('bairro', bairro);

  window.location.href = '/imoveis/?' + params.toString();
}

// ─── CAPTAÇÃO FORM ─────────────────────
function enviarCaptacao() {
  const nome   = document.getElementById('cap-nome')?.value?.trim();
  const wpp    = document.getElementById('cap-wpp')?.value?.trim();
  const tipo   = document.getElementById('cap-tipo')?.value;
  const bairro = document.getElementById('cap-bairro')?.value?.trim();
  const valor  = document.getElementById('cap-valor')?.value?.trim();
  const msgDiv = document.getElementById('mr-captacao-msg');
  const btn    = document.querySelector('.mr-btn-captacao');

  if (!nome || !wpp) {
    showMsg(msgDiv, 'Preencha seu nome e WhatsApp.', 'err');
    return;
  }

  btn.textContent = 'Enviando...';
  btn.disabled = true;

  const data = new FormData();
  data.append('action', 'marcos_rosa_captacao');
  data.append('nonce',  marcosRosa.nonce);
  data.append('nome',   nome);
  data.append('whatsapp', wpp);
  data.append('tipo',   tipo);
  data.append('bairro', bairro);
  data.append('valor',  valor);

  fetch(marcosRosa.ajaxurl, { method: 'POST', body: data })
    .then(r => r.json())
    .then(res => {
      if (res.success) {
        showMsg(msgDiv, res.data.msg, 'ok');
        // Abre WhatsApp do proprietário automaticamente
        setTimeout(() => window.open(res.data.wpp_link, '_blank'), 1500);
        // Limpa form
        ['cap-nome','cap-wpp','cap-bairro','cap-valor'].forEach(id => {
          const el = document.getElementById(id);
          if (el) el.value = '';
        });
        document.getElementById('cap-tipo').value = '';
      } else {
        showMsg(msgDiv, res.data?.msg || 'Erro ao enviar.', 'err');
      }
    })
    .catch(() => showMsg(msgDiv, 'Erro de conexão. Tente pelo WhatsApp.', 'err'))
    .finally(() => {
      btn.textContent = '📲 Quero Anunciar Meu Imóvel';
      btn.disabled = false;
    });
}

function showMsg(el, msg, tipo) {
  if (!el) return;
  el.style.display = 'block';
  el.className = tipo === 'ok' ? 'mr-captacao-msg-ok' : 'mr-captacao-msg-err';
  el.textContent = msg;
  setTimeout(() => { el.style.display = 'none'; }, 6000);
}
