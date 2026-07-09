(function () {
  'use strict';

  var ns = window.WizardState;
  var H = window.WizardHelpers;
  var P = window.WizardPricing;

  function cardClickHandler(el, containerId, group, key) {
    var cards = document.querySelectorAll('#' + containerId + ' .ead-select-card');
    var wasSelected = el.classList.contains('selected');

    cards.forEach(function (c) { c.classList.remove('selected'); });

    if (wasSelected) {
      delete ns.selections[key];
      var nextId = getNextBtnForContainer(containerId);
      if (nextId) {
        var nextBtn = document.getElementById(nextId);
        if (nextBtn) nextBtn.disabled = true;
      }
      return;
    }

    el.classList.add('selected');
    ns.selections[key] = parseInt(el.dataset.value);
    if (group) ns.selections[key] = el.dataset.group || null;

    if (key === 'servicio_id') {
      showServicioDetalle(parseInt(el.dataset.value));
    }
    if (key === 'nivel_suciedad_id') {
      onSuciedadSelected();
    }

    var nextId = getNextBtnForContainer(containerId);
    if (nextId) {
      var nextBtn = document.getElementById(nextId);
      if (nextBtn) nextBtn.disabled = false;
    }
  }

  function getNextBtnForContainer(containerId) {
    var map = {
      'serviciosContainer': 'btnNext',
      'paquetesContainer': 'btnNext',
      'tiposVehiculoContainer': 'btnNext2',
      'segmentosContainer': 'btnNext2',
    };
    return map[containerId] || 'btnNext';
  }

  function onSuciedadSelected() {
    renderAdicionalesFiltrados(ns.selections.servicio_id);
    if (ns.selections.servicio_id && ns.selections.tipo_vehiculo_id && ns.selections.segmento_id) {
      if (P) P.fetchPrecio();
    }
    if (window.WizardSummary) window.WizardSummary.renderResumen();
  }

  function renderCards(containerId, items, labelKey, descKey, iconKey, selectionKey) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var selectedVal = ns.selections[selectionKey];
    var html = '';
    items.forEach(function (item) {
      var selected = selectedVal === item.id ? ' selected' : '';
      var icon = iconKey && item[iconKey] ? '<i class="' + H.escapeHtml(item[iconKey]) + '" aria-hidden="true"></i>' : '';
      var desc = descKey && item[descKey] ? '<small>' + H.escapeHtml(item[descKey]) + '</small>' : '';
      html += '<div class="ead-select-card' + selected + '" data-value="' + item.id + '" tabindex="0" role="radio" aria-checked="' + (selected ? 'true' : 'false') + '"' +
        ' onclick="window.WizardRendering.cardClick(this,\'' + containerId + '\',\'\',\'' + selectionKey + '\')"' +
        ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();this.click();}">' +
        icon + '<span>' + H.escapeHtml(item[labelKey]) + '</span>' + desc + '</div>';
    });
    container.innerHTML = html;
    hideLoadingFor(containerId);
  }

  function hideLoadingFor(containerId) {
    var map = {
      'tiposVehiculoContainer': 'tiposVehiculoLoading',
      'segmentosContainer': 'segmentosLoading',
      'serviciosContainer': 'serviciosLoading',
      'paquetesContainer': 'paquetesLoading',
    };
    var loadId = map[containerId];
    if (loadId) { var el = document.getElementById(loadId); if (el) el.style.display = 'none'; }
  }

  function renderPaqueteComposicion(svcId) {
    var el = document.getElementById('paqueteComposicion');
    if (!el) return;
    if (!svcId) { el.style.display = 'none'; return; }
    var allSvcs = (ns.servicios.paquete || []).concat(ns.servicios.base || []);
    var svc = allSvcs.find(function (x) { return x.id === svcId; });
    if (!svc || svc.tipo !== 'paquete' || !svc.composicion) { el.style.display = 'none'; return; }
    el.style.display = 'block';
    var comps = svc.composicion.sort(function (a, b) { return a.orden - b.orden; });
    var html = '<div class="p-2 rounded" style="background:var(--color-brand-tint);border:1px solid rgba(26,107,255,0.2);">' +
      '<i class="fa-solid fa-cube text-primary me-2"></i><strong>Incluye:</strong> ';
    html += comps.map(function (c) {
      return '<span class="badge me-1" style="background:var(--color-brand-tint);color:var(--color-brand);">' +
        (c.es_principal ? '<i class="fa-solid fa-star me-1"></i>' : '') + H.escapeHtml(c.nombre) + '</span>';
    }).join(' ');
    html += '</div>';
    el.innerHTML = html;
  }

  // ─── ADICIONALES AS CHIPS ───
  function renderAdicionalesFiltrados(svcId) {
    var container = document.getElementById('adicionalesContainer') || document.getElementById('adicionalesChips');
    var target = container || document.getElementById('adicionalesContainer');
    if (!target) return;
    if (!svcId) { target.innerHTML = '<p class="text-muted small">Selecciona un servicio primero.</p>'; return; }
    var adicionales = ns.servicios.adicional || [];
    if (!adicionales.length) {
      target.innerHTML = '<p class="text-muted small">No hay adicionales disponibles.</p>';
      return;
    }
    var html = '<div class="ad-chips">';
    adicionales.forEach(function (ad) {
      var checked = (ns.selections.adicionales_ids || []).indexOf(ad.id) !== -1;
      html += '<button type="button" class="ad-chip' + (checked ? ' active' : '') + '" data-id="' + ad.id + '"' +
        ' onclick="WizardRendering.toggleAdicionalChip(this,' + ad.id + ')"' +
        (ad.descripcion ? ' title="' + H.escapeHtml(ad.descripcion) + '"' : '') + '>' +
        H.escapeHtml(ad.nombre) + '</button>';
    });
    html += '</div>';
    target.innerHTML = html;
  }

  function renderInspeccionAviso(svcId) {
    var el = document.getElementById('inspeccionAviso');
    if (!el) return;
    if (!svcId) { el.style.display = 'none'; return; }
    var allSvcs = (ns.servicios.base || []).concat(ns.servicios.paquete || []);
    var svc = allSvcs.find(function (x) { return x.id === svcId; });
    if (svc && svc.requiere_inspeccion_previa) {
      el.style.display = 'block';
      el.innerHTML =
        '<div class="p-2 rounded" style="background:var(--color-warning-tint);border:1px solid rgba(224,164,41,0.3);">' +
        '<i class="fa-solid fa-magnifying-glass text-warning me-2"></i>' +
        '<span style="color:var(--color-warning);font-size:var(--text-caption);">Este servicio requiere inspeccion previa. El precio definitivo se confirmara tras evaluar el vehiculo.</span></div>';
    } else { el.style.display = 'none'; el.innerHTML = ''; }
  }

  // ─── PREMIUM SERVICE CARDS ───
  function renderServiceCardPremium(s, idxInCat, totalInCat) {
    var selected = ns.selections.servicio_id === s.id ? ' selected' : '';
    var descShort = s.descripcion ? '<p class="svc-desc">' + H.escapeHtml(s.descripcion) + '</p>' : '';
    var precioText = s.precio_desde ? '<span class="svc-price">Gs ' + String(s.precio_desde).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '</span>' : '';
    var duracionText = s.duracion_estimada ? '<span class="svc-dur"><i class="fa-regular fa-clock"></i> ' + s.duracion_estimada + ' min</span>' : '';

    var badge = '';
    if (idxInCat === 0 && totalInCat > 1) {
      badge = '<span class="svc-badge popular">Mas solicitado</span>';
    } else if (idxInCat === 0 && totalInCat === 1) {
      // Single item in category
    }

    return '<div class="svc-card' + selected + '" data-value="' + s.id + '" tabindex="0" role="radio" aria-checked="' + (selected ? 'true' : 'false') + '"' +
      ' onclick="window.WizardRendering.cardClick(this,\'serviciosContainer\',\'\',\'servicio_id\')"' +
      ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();this.click();}">' +
      badge +
      '<div class="svc-card-header"><span class="svc-card-name">' + H.escapeHtml(s.nombre) + '</span>' +
      '<div class="svc-card-meta">' + precioText + (precioText && duracionText ? '<span class="svc-sep"></span>' : '') + duracionText + '</div></div>' +
      descShort +
      '</div>';
  }

  // ─── INLINE DETAIL PANEL ───
  function showServicioDetalle(svcId) {
    var panel = document.getElementById('servicioDetalle');
    if (!panel) return;
    panel.style.display = 'block';
    var content = document.getElementById('svcDetailContent');
    if (!content) return;

    var allSvcs = (ns.servicios.base || []).concat(ns.servicios.paquete || []);
    var svc = allSvcs.find(function (x) { return x.id === svcId; });
    if (!svc) { panel.style.display = 'none'; return; }

    // Suciedad icons
    var suciedadIcons = { 1: 'fa-droplet', 2: 'fa-droplet', 3: 'fa-droplet' };
    var suciedad = ns.nivelesSuciedad;
    var suciedadHtml = '';
    if (suciedad.length) {
      suciedadHtml = '<label class="form-label">Nivel de Suciedad</label><div class="suciedad-pills">';
      suciedad.forEach(function (n, i) {
        var sel = ns.selections.nivel_suciedad_id === n.id ? ' active' : '';
        var icon = i === 0 ? 'fa-droplet' : (i === 1 ? 'fa-droplet' : 'fa-droplet');
        var style = i === 0 ? 'style="opacity:0.6"' : (i === 1 ? 'style="opacity:0.8"' : '');
        // Use text indicator for severity
        var sev = i === 0 ? '' : (i === suciedad.length - 1 ? ' ◆◆◆' : (i === 1 ? ' ◆' : ''));
        suciedadHtml += '<button type="button" class="suciedad-pill' + sel + '" data-value="' + n.id + '"' +
          ' onclick="WizardRendering.selectSuciedadPill(this,' + n.id + ')"><i class="fa-solid ' + icon + '" ' + style + '></i> ' + H.escapeHtml(n.nombre) + sev + '</button>';
      });
      suciedadHtml += '</div>';
    }

    content.innerHTML =
      '<h3 class="svc-detail-name">' + H.escapeHtml(svc.nombre) + '</h3>' +
      (svc.descripcion ? '<p class="svc-detail-desc">' + H.escapeHtml(svc.descripcion) + '</p>' : '') +
      suciedadHtml +
      '<label class="form-label mt-2">Adicionales (opcional)</label>' +
      '<div id="adicionalesChips"></div>';

    // Render adicionales into the chip container
    renderAdicionalesFiltrados(svcId);

    // Trigger pricing
    if (ns.selections.nivel_suciedad_id && ns.selections.tipo_vehiculo_id && ns.selections.segmento_id) {
      if (P) P.fetchPrecio();
    }
    if (window.WizardSummary) window.WizardSummary.renderResumen();
  }

  // ─── CATEGORY ACCORDION ───
  function renderServiciosBase() {
    var items = ns.servicios.base || [];
    var container = document.getElementById('serviciosContainer');
    if (!container) return;
    if (!items.length) {
      container.innerHTML = '<p class="text-muted">No hay servicios disponibles.</p>';
      hideLoadingFor('serviciosContainer');
      return;
    }
    var categorias = {};
    items.forEach(function (s) {
      var cat = s.categoria_nombre || 'General';
      if (!categorias[cat]) categorias[cat] = [];
      categorias[cat].push(s);
    });
    var catKeys = Object.keys(categorias).sort();
    var selectedSvcId = ns.selections.servicio_id;
    var html = '';
    var catIcons = {
      'Paquetes': 'fa-solid fa-cube', 'Lavados': 'fa-solid fa-droplet',
      'Detallados': 'fa-solid fa-sparkles', 'Tratamientos': 'fa-solid fa-shield-halved',
      'Express': 'fa-solid fa-bolt', 'Premium': 'fa-solid fa-gem',
    };
    catKeys.forEach(function (cat) {
      var iconClass = catIcons[cat] || 'fa-solid fa-wrench';
      var safeId = 'cat-' + cat.replace(/[^a-z0-9]/gi, '').toLowerCase();
      var isOpen = false;
      var hasSelected = categorias[cat].some(function (s) { return s.id === selectedSvcId; });
      if (hasSelected) isOpen = true;
      if (!selectedSvcId && catKeys.indexOf(cat) === 0) isOpen = true;

      html += '<div class="cat-accordion-header' + (isOpen ? ' active' : '') + '" onclick="WizardRendering.toggleCategory(\'' + safeId + '\')" data-cat="' + safeId + '">';
      html += '<span class="cat-name"><i class="' + iconClass + '"></i>' + H.escapeHtml(cat) + '</span>';
      html += '<i class="fa-solid fa-chevron-down cat-chevron"></i></div>';
      html += '<div class="cat-accordion-body' + (isOpen ? ' open' : '') + '" id="' + safeId + '">';
      html += '<div class="svc-list">';
      var catItems = categorias[cat];
      catItems.forEach(function (s, idx) {
        html += renderServiceCardPremium(s, idx, catItems.length);
      });
      html += '</div></div>';
    });
    container.innerHTML = html;
    hideLoadingFor('serviciosContainer');

    // Restore detail panel if service selected
    if (selectedSvcId) showServicioDetalle(selectedSvcId);
  }

  function renderNivelesSuciedad() {
    var items = ns.nivelesSuciedad;
    if (!items.length) return;
    renderCards('nivelesSuciedadContainer', items, 'nombre', 'descripcion', null, 'nivel_suciedad_id');
  }

  // ─── API ───
  window.WizardRendering = {
    cardClick: cardClickHandler,
    toggleCategory: function (safeId) {
      var hdr = document.querySelector('.cat-accordion-header[data-cat="' + safeId + '"]');
      var body = document.getElementById(safeId);
      if (!hdr || !body) return;
      var isOpen = body.classList.contains('open');
      document.querySelectorAll('.cat-accordion-body').forEach(function (b) { b.classList.remove('open'); });
      document.querySelectorAll('.cat-accordion-header').forEach(function (h) { h.classList.remove('active'); });
      if (!isOpen) { body.classList.add('open'); hdr.classList.add('active'); }
    },
    selectSuciedadPill: function (el, id) {
      document.querySelectorAll('.suciedad-pill').forEach(function (p) { p.classList.remove('active'); });
      el.classList.add('active');
      ns.selections.nivel_suciedad_id = id;
      renderAdicionalesFiltrados(ns.selections.servicio_id);
      if (ns.selections.servicio_id && ns.selections.tipo_vehiculo_id && ns.selections.segmento_id) {
        if (P) P.fetchPrecio();
      }
      updatePrecioBadgeDetail();
      if (window.WizardSummary) window.WizardSummary.renderResumen();
    },
    toggleAdicionalChip: function (el, adId) {
      var adIds = ns.selections.adicionales_ids || [];
      if (adIds.indexOf(adId) === -1) {
        adIds.push(adId);
        el.classList.add('active');
      } else {
        adIds = adIds.filter(function (x) { return x !== adId; });
        el.classList.remove('active');
      }
      ns.selections.adicionales_ids = adIds;
      if (P) P.fetchPrecio();
      updatePrecioBadgeDetail();
      if (window.WizardSummary) window.WizardSummary.renderResumen();
    },
    onAdicionalToggle: function (el, adId) {
      var adIds = ns.selections.adicionales_ids || [];
      if (el.checked) { if (adIds.indexOf(adId) === -1) adIds.push(adId); }
      else { adIds = adIds.filter(function (x) { return x !== adId; }); }
      ns.selections.adicionales_ids = adIds;
      if (P) P.fetchPrecio();
      if (window.WizardSummary) window.WizardSummary.renderResumen();
    },

    showServicioDetalle: showServicioDetalle,

    renderTiposVehiculo: function () {
      var items = ns.tiposVehiculo;
      if (!items.length) return;
      renderCards('tiposVehiculoContainer', items, 'nombre', 'descripcion', 'icono', 'tipo_vehiculo_id');
    },

    renderSegmentos: function () {
      var items = ns.segmentos;
      if (!items.length) return;
      renderCards('segmentosContainer', items, 'nombre', 'descripcion', null, 'segmento_id');
    },

    renderNivelesSuciedad: renderNivelesSuciedad,
    renderServiciosBase: renderServiciosBase,

    renderPaquetes: function () {
      var items = ns.servicios.paquete || [];
      var container = document.getElementById('paquetesContainer');
      if (!container) return;
      if (!items.length) { container.innerHTML = ''; return; }
      var html = '<div class="cat-accordion-header active" onclick="WizardRendering.toggleCategory(\'cat-paquetes\')" data-cat="cat-paquetes">' +
        '<span class="cat-name"><i class="fa-solid fa-cube"></i>Paquetes</span>' +
        '<i class="fa-solid fa-chevron-down cat-chevron"></i></div>' +
        '<div class="cat-accordion-body open" id="cat-paquetes"><div class="svc-list">';
      items.forEach(function (pkg) {
        var selected = ns.selections.servicio_id === pkg.id ? ' selected' : '';
        var compsHtml = pkg.composicion ? '<p class="svc-desc">' + pkg.composicion.map(function (c) { return c.nombre; }).join(' + ') + '</p>' : '';
        var diasHtml = (pkg.requiere_varios_dias && pkg.dias_bloqueo) ? '<span class="svc-dur" style="color:var(--color-warning);">' + pkg.dias_bloqueo + ' dias</span>' : '';
        html += '<div class="svc-card' + selected + '" data-value="' + pkg.id + '" tabindex="0" role="radio" aria-checked="' + (selected ? 'true' : 'false') + '"' +
          ' onclick="window.WizardRendering.cardClick(this,\'paquetesContainer\',\'\',\'servicio_id\')"' +
          ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();this.click();}">' +
          '<span class="svc-badge package">Paquete</span>' +
          '<div class="svc-card-header"><span class="svc-card-name">' + H.escapeHtml(pkg.nombre) + '</span>' +
          '<div class="svc-card-meta">' + diasHtml + '</div></div>' + compsHtml +
          '</div>';
      });
      html += '</div></div>';
      container.innerHTML = html;
    },

    renderAdicionalesFiltrados: renderAdicionalesFiltrados,
    renderPaqueteComposicion: renderPaqueteComposicion,
    renderInspeccionAviso: renderInspeccionAviso,

    renderPrecioBadge: function () {
      updatePrecioBadgeDetail();
    },

    highlightTipoSegmento: function (tipoId, segId) {
      ['tiposVehiculoContainer', 'segmentosContainer'].forEach(function (cid) {
        var cards = document.querySelectorAll('#' + cid + ' .ead-select-card');
        cards.forEach(function (c) {
          c.classList.remove('selected');
          var val = parseInt(c.dataset.value);
          if ((cid === 'tiposVehiculoContainer' && val === tipoId) || (cid === 'segmentosContainer' && val === segId)) {
            c.classList.add('selected');
          }
        });
      });
    },
  };

  var _lastPrecio = 0;

  function animatePrice(el, target) {
    var start = _lastPrecio;
    if (start === target) return;
    var duration = 350;
    var startTime = performance.now();

    function tick(now) {
      var t = Math.min((now - startTime) / duration, 1);
      var current = Math.round(start + (target - start) * t);
      el.innerHTML =
        '<span class="fs-5 fw-bold" style="color:var(--accent);">' + H.formatGuarani(current) + '</span>' +
        '<span class="ms-2 text-muted"><i class="fa-regular fa-clock me-1"></i>' + H.formatearDuracion(ns.precio ? ns.precio.duracion_minutos : 0) + '</span>';
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    _lastPrecio = target;
  }

  function updatePrecioBadgeDetail() {
    var el = document.getElementById('precioBadgeDetail');
    if (!el) return;
    var p = ns.precio;
    if (!p) {
      _lastPrecio = 0;
      el.innerHTML = '<span class="text-muted">Selecciona el nivel de suciedad para ver el precio</span>';
      return;
    }
    animatePrice(el, p.precio);
  }
})();
