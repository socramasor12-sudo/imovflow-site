/* Marcos Rosa Corretor - main.js */
(function () {
    'use strict';

    /* =========================================================
       Header scroll effect
    ========================================================= */
    var header = document.getElementById('site-header');

    function onScroll() {
        if (window.scrollY > 80) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }

    if (header) {
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    /* =========================================================
       Mobile menu toggle
    ========================================================= */
    var menuToggle = document.querySelector('.menu-toggle');
    var navList    = document.querySelector('.nav-list');

    if (menuToggle && navList) {
        menuToggle.addEventListener('click', function () {
            var isOpen = navList.classList.toggle('is-open');
            menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            menuToggle.classList.toggle('is-active', isOpen);
        });

        // Close menu when a nav link is clicked
        navList.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navList.classList.remove('is-open');
                menuToggle.setAttribute('aria-expanded', 'false');
                menuToggle.classList.remove('is-active');
            });
        });
    }

    /* =========================================================
       Smooth scroll for anchor links
    ========================================================= */
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href').slice(1);
            var target   = document.getElementById(targetId);

            if (target) {
                e.preventDefault();
                var headerHeight = header ? header.offsetHeight : 0;
                var top = target.getBoundingClientRect().top + window.scrollY - headerHeight;

                window.scrollTo({ top: top, behavior: 'smooth' });
            }
        });
    });

    /* =========================================================
       Busca (search form)
    ========================================================= */
    window.buscar = function (e) {
        e.preventDefault();

        var finalidade = document.getElementById('finalidade').value;
        var tipo       = document.getElementById('tipo').value;
        var bairro     = document.getElementById('bairro').value.trim();

        var params = new URLSearchParams();
        if (finalidade) params.set('finalidade', finalidade);
        if (tipo)       params.set('tipo', tipo);
        if (bairro)     params.set('bairro', bairro);

        var url = '/imoveis/';
        if (params.toString()) {
            url += '?' + params.toString();
        }

        window.location.href = url;
    };

    /* =========================================================
       Captação form – AJAX submit
    ========================================================= */
    var captacaoForm     = document.getElementById('captacao-form');
    var captacaoFeedback = document.getElementById('captacao-feedback');

    window.enviarCaptacao = function (formData) {
        if (!window.marcosRosa || !window.marcosRosa.ajaxurl) {
            showFeedback('error', 'Erro de configuração. Por favor, tente novamente.');
            return;
        }

        formData.append('action', 'captacao');
        formData.append('nonce',  window.marcosRosa.nonce);

        fetch(window.marcosRosa.ajaxurl, {
            method: 'POST',
            body:   formData,
        })
            .then(function (res) {
                if (!res.ok) throw new Error('Erro de rede');
                return res.json();
            })
            .then(function (data) {
                if (data.success) {
                    showFeedback('success', data.data.message || 'Solicitação enviada com sucesso!');
                    captacaoForm.reset();
                } else {
                    showFeedback('error', data.data.message || 'Erro ao enviar. Tente novamente.');
                }
            })
            .catch(function () {
                showFeedback('error', 'Erro de conexão. Verifique sua internet e tente novamente.');
            });
    };

    if (captacaoForm) {
        captacaoForm.addEventListener('submit', function (e) {
            e.preventDefault();

            var submitBtn = captacaoForm.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled    = true;
                submitBtn.textContent = 'Enviando...';
            }

            var formData = new FormData(captacaoForm);
            enviarCaptacao(formData);

            if (submitBtn) {
                setTimeout(function () {
                    submitBtn.disabled    = false;
                    submitBtn.textContent = 'Solicitar Avaliação Gratuita';
                }, 3000);
            }
        });
    }

    function showFeedback(type, message) {
        if (!captacaoFeedback) return;
        captacaoFeedback.className  = 'form-feedback form-feedback--' + type;
        captacaoFeedback.textContent = message;
        captacaoFeedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

}());
