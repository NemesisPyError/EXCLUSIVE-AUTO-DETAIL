(function () {
  'use strict';

  var ns = window.WizardState;
  var H = window.WizardHelpers;
  var isMobile = function () { return window.innerWidth < (window.WIZARD_MOBILE_BP || 768); };

  function findTyped(items, id) { return (items || []).find(function (t) { return t.id === id; }); }

  function getServiceName() {
    var allSvcs = (ns.servicios.base || []).concat(ns.servicios.paquete || []);
    var svc = allSvcs.find(function (x) { return x.id === ns.selections.servicio_id; });
    return svc ? svc.nombre : '';
  }

  function renderResumen() {
    var sidebar = document.getElementById('resumenSidebar');
    var msfPrice = document.getElementById('msfPrice');
    var msfFooter = document.getElementById('mobileStickyFooter');
    var s = ns.selections;
    var mobile = isMobile();
    var hasContent = s.servicio_id || s.tipo_vehiculo_id;

    if (sidebar) {
      if (!hasContent) {
        sidebar.innerHTML = '<p class="text-muted-custom small">Selecciona un servicio para comenzar.</p>';
      } else {
        var tv = findTyped(ns.tiposVehiculo, s.tipo_vehiculo_id);
        var seg = findTyped(ns.segmentos, s.segmento_id);
        var niv = findTyped(ns.nivelesSuciedad, s.nivel_suciedad_id);
        var lines = [];
        lines.push(bsItem('Servicio', getServiceName() || '—'));
        lines.push(bsItem('Vehiculo', (s.marca + ' ' + s.modelo).trim() + (tv ? ' — ' + tv.nombre : '') + (seg ? ' ' + seg.nombre : '') || '—'));
        if (niv) lines.push(bsItem('Suciedad', niv.nombre));
        if (s.fecha && s.hora_inicio) lines.push(bsItem('Agenda', s.fecha + ' ' + s.hora_inicio + ' (' + H.formatearDuracion(ns.duracion) + ')'));

        if (ns.precio) {
          lines.push('<div class="bs-item"><div class="bs-item-label">Precio</div><div class="bs-item-value price">' + H.formatGuarani(ns.precio.precio) + '</div></div>');
        }
        sidebar.innerHTML = lines.join('') || '<p class="text-muted-custom small">Completa los pasos.</p>';
      }
    }

    if (mobile && msfFooter && msfPrice) {
      if (hasContent && ns.precio) {
        msfFooter.style.display = 'flex';
        msfPrice.innerHTML = '<span class="msf-amount">' + H.formatGuarani(ns.precio.precio) + '</span>';
      } else if (hasContent) {
        msfFooter.style.display = 'flex';
        msfPrice.innerHTML = '<span style="color:var(--text-dim);font-size:0.78rem;">Calculando...</span>';
      } else {
        msfFooter.style.display = 'none';
      }
    } else if (!mobile && msfFooter) {
      msfFooter.style.display = 'none';
    }

    updateBottomSheet();
  }

  function bsItem(label, value) {
    return '<div class="bs-item"><div class="bs-item-label">' + H.escapeHtml(label) + '</div><div class="bs-item-value">' + H.escapeHtml(value) + '</div></div>';
  }

  function openBottomSheet() {
    var sheet = document.getElementById('bottomSheet');
    var overlay = document.getElementById('bsOverlay');
    if (sheet) sheet.classList.add('show');
    if (overlay) overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
    updateBottomSheet();
  }

  function closeBottomSheet() {
    var sheet = document.getElementById('bottomSheet');
    var overlay = document.getElementById('bsOverlay');
    if (sheet) sheet.classList.remove('show');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
  }

  function updateBottomSheet() {
    var body = document.getElementById('bsBody');
    if (!body) return;
    var s = ns.selections;
    if (!s.servicio_id && !s.tipo_vehiculo_id) {
      body.innerHTML = '<p class="text-muted-custom small">Selecciona un servicio para comenzar.</p>';
      return;
    }
    var tv = findTyped(ns.tiposVehiculo, s.tipo_vehiculo_id);
    var seg = findTyped(ns.segmentos, s.segmento_id);
    var niv = findTyped(ns.nivelesSuciedad, s.nivel_suciedad_id);
    var lines = [];
    lines.push(bsItem('Servicio', getServiceName() || '—'));
    lines.push(bsItem('Vehiculo', (s.marca + ' ' + s.modelo).trim() + (tv ? ' (' + tv.nombre + (seg ? ', ' + seg.nombre : '') + ')' : '') || '—'));
    if (niv) lines.push(bsItem('Suciedad', niv.nombre));
    if (s.fecha && s.hora_inicio) lines.push(bsItem('Agenda', s.fecha + ' a las ' + s.hora_inicio + ' (' + H.formatearDuracion(ns.duracion) + ')'));
    if (ns.precio) {
      lines.push('<div class="bs-item"><div class="bs-item-label">Precio Total</div><div class="bs-item-value price">' + H.formatGuarani(ns.precio.precio) + '</div></div>');
    }
    body.innerHTML = lines.join('') || '<p class="text-muted-custom small">Completa los pasos.</p>';
  }

  // ─── STEP 5 SUMMARY with price breakdown toggle ───
  function renderStep5Summary() {
    var el = document.getElementById('step5Summary');
    if (!el) return;
    var s = ns.selections;
    var total = ns.precio ? ns.precio.precio : 0;
    var svcName = getServiceName();
    var niv = findTyped(ns.nivelesSuciedad, s.nivel_suciedad_id);
    var tv = findTyped(ns.tiposVehiculo, s.tipo_vehiculo_id);
    var seg = findTyped(ns.segmentos, s.segmento_id);

    var btnSubmit = document.getElementById('btnSubmit');
    if (btnSubmit) btnSubmit.disabled = false;

    var rows = '';
    rows += s5row('Cliente', (s.nombre + ' ' + s.apellido).trim() || '—');
    if (s.telefono) rows += s5row('Telefono', s.telefono);
    if (s.email) rows += s5row('Email', s.email);
    var vehiculo = (s.marca + ' ' + s.modelo).trim();
    if (tv) vehiculo += ' — ' + tv.nombre;
    if (seg) vehiculo += ', ' + seg.nombre;
    if (s.anio) vehiculo += ' (' + s.anio + ')';
    if (s.color) vehiculo += ' — ' + s.color;
    rows += s5row('Vehiculo', vehiculo || '—');
    rows += s5row('Servicio', svcName + (niv ? ' — ' + niv.nombre : ''));
    rows += s5row('Duracion', H.formatearDuracion(ns.duracion));
    if (s.fecha && s.hora_inicio) rows += s5row('Agenda', s.fecha + ' a las ' + s.hora_inicio);

    // Price with breakdown toggle
    var priceBreakdown = '';
    if (ns.precio) {
      priceBreakdown = '<div class="s5-section"><span class="s5-section-label">Precio</span>' +
        '<span class="s5-section-value s5-price">' + H.formatGuarani(total) + '</span></div>';

      // Breakdown (collapsed by default)
      priceBreakdown += '<button type="button" class="price-breakdown-toggle" onclick="WizardSummary.toggleBreakdown()">' +
        '<i class="fa-solid fa-chevron-down me-1"></i>Ver desglose</button>';
      priceBreakdown += '<div class="price-breakdown" id="priceBreakdown" style="display:none;">';
      priceBreakdown += '<div class="pb-row"><span>Servicio base</span><span>Gs ' + String(ns.precio.precio || 0).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '</span></div>';
      if ((ns.selections.adicionales_ids || []).length) {
        priceBreakdown += '<div class="pb-row"><span>Adicionales</span><span class="text-muted">incluido</span></div>';
      }
      priceBreakdown += '<div class="pb-row pb-total"><span>Total</span><span>' + H.formatGuarani(total) + '</span></div>';
      priceBreakdown += '</div>';
    }

    el.innerHTML = '<div class="s5-compact">' + rows + priceBreakdown + '</div>';
  }

  function s5row(label, value) {
    return '<div class="s5-section"><span class="s5-section-label">' + H.escapeHtml(label) + '</span><span class="s5-section-value">' + H.escapeHtml(value) + '</span></div>';
  }

  function toggleBreakdown() {
    var el = document.getElementById('priceBreakdown');
    var btn = document.querySelector('.price-breakdown-toggle');
    if (!el || !btn) return;
    var hidden = el.style.display === 'none';
    el.style.display = hidden ? 'block' : 'none';
    btn.innerHTML = hidden ?
      '<i class="fa-solid fa-chevron-up me-1"></i>Ocultar desglose' :
      '<i class="fa-solid fa-chevron-down me-1"></i>Ver desglose';
  }

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { renderResumen(); }, 100);
  });

  window.WizardSummary = {
    renderResumen: renderResumen,
    renderStep5Summary: renderStep5Summary,
    openBottomSheet: openBottomSheet,
    closeBottomSheet: closeBottomSheet,
    updateBottomSheet: updateBottomSheet,
    toggleBreakdown: toggleBreakdown,
  };
})();
