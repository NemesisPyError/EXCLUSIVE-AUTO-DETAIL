(function () {
    'use strict';

    // =============================================
    // AOS — Animate On Scroll
    // =============================================
    AOS.init({
        once: true,
        offset: 80,
        duration: 800,
        easing: 'ease-out',
    });

    // =============================================
    // NAVBAR — Cambio de opacidad al hacer scroll
    // =============================================
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        const checkScroll = function () {
            if (window.scrollY > 60) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        };
        window.addEventListener('scroll', checkScroll, { passive: true });
        checkScroll();
    }

    // =============================================
    // SMOOTH SCROLL — Anclas del navbar
    // =============================================
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetEl = document.querySelector(targetId);
            if (!targetEl) return;

            e.preventDefault();

            // Cerrar menú mobile si está abierto
            var navCollapse = document.getElementById('navbarNav');
            if (navCollapse && navCollapse.classList.contains('show')) {
                var bsCollapse = bootstrap.Collapse.getInstance(navCollapse);
                if (bsCollapse) bsCollapse.hide();
            }

            var offsetTop = targetEl.getBoundingClientRect().top + window.pageYOffset - 70;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth',
            });
        });
    });

    // =============================================
    // FILTRO DE SERVICIOS POR CATEGORÍA
    // =============================================
    var filterBtns = document.querySelectorAll('.filter-btn');
    var serviceItems = document.querySelectorAll('.service-item');

    if (filterBtns.length && serviceItems.length) {
        filterBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                filterBtns.forEach(function (b) { b.classList.remove('active'); });
                this.classList.add('active');

                var categoria = this.getAttribute('data-filter');

                serviceItems.forEach(function (item) {
                    if (categoria === 'todos' || item.getAttribute('data-categoria') === categoria) {
                        item.style.display = 'block';
                        item.style.opacity = '0';
                        setTimeout(function () {
                            item.style.opacity = '1';
                        }, 20);
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // =============================================
    // AÑO DINÁMICO EN EL FOOTER
    // =============================================
    var yearSpan = document.querySelector('.footer-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

})();
