(function () {
  'use strict';

  var ns = window.WizardState;
  var API = window.WizardAPI;
  var H = window.WizardHelpers;

  var searchTimer = null;
  var abortController = null;

  function debounce(fn, ms) {
    return function () {
      var ctx = this, args = arguments;
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  function init() {
    var inp = document.getElementById('autoMarca');
    if (!inp) return;
    inp.addEventListener('input', debounce(searchMarcas, 250));
    inp.addEventListener('focus', function () { if (inp.value) searchMarcas(); });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.ead-autocomplete-wrapper')) {
        closeDropdown('marcaDropdown');
        closeDropdown('modeloDropdown');
      }
    });
    var inpM = document.getElementById('autoModelo');
    if (inpM) {
      inpM.addEventListener('input', debounce(searchModelos, 250));
    }
  }

  function searchMarcas() {
    var q = (document.getElementById('autoMarca') || {}).value || '';
    if (q.length < 1) { closeDropdown('marcaDropdown'); return; }
    if (abortController) abortController.abort();
    abortController = new AbortController();
    API.fetchMarcas(q).then(function (data) {
      if (!data.success) { console.warn('fetchMarcas: success=false', data); return; }
      renderDropdown('marcaDropdown', 'autoMarca', data.marcas || [], 'nombre', function (item) {
        selectMarca(item);
      });
    }).catch(function (err) {
      console.warn('fetchMarcas error:', err);
    });
  }

  function selectMarca(item) {
    ns.selections.marca_id = item.id;
    ns.selections.marca = item.nombre;
    document.getElementById('autoMarca').value = item.nombre;
    closeDropdown('marcaDropdown');
    document.getElementById('autoModelo').value = '';
    document.getElementById('autoModelo').focus();
    ns.selections.modelo_id = null;
    ns.selections.modelo = '';
    updateVehicleInfo();
  }

  function searchModelos() {
    var q = (document.getElementById('autoModelo') || {}).value || '';
    var marcaId = ns.selections.marca_id;
    if (q.length < 1 && !marcaId) { closeDropdown('modeloDropdown'); return; }

    if (abortController) abortController.abort();
    abortController = new AbortController();

    API.fetchModelos(q, marcaId).then(function (data) {
      if (!data.success) return;

      var modelos = data.modelos || [];
      if (modelos.length > 0) {
        renderDropdown('modeloDropdown', 'autoModelo', modelos, 'nombre', function (item) {
          selectModelo(item);
        }, function (item) {
          return (item.marca_nombre ? '<small class="d-block" style="color:var(--color-text-tertiary);font-size:var(--text-caption);">' +
            H.escapeHtml(item.marca_nombre) + ' | ' + H.escapeHtml(item.tipo_vehiculo_nombre || '') +
            ' | ' + H.escapeHtml(item.segmento_nombre || '') + '</small>' : '');
        });
        hideNotCatalogued();
      } else if (q.length >= 2) {
        closeDropdown('modeloDropdown');
        showNotCatalogued();
      }
    }).catch(function () {});
  }

  function selectModelo(item) {
    ns.selections.modelo_id = item.id;
    ns.selections.modelo = item.nombre;
    ns.selections.tipo_vehiculo_id = item.tipo_vehiculo_id;
    ns.selections.segmento_id = item.segmento_id;
    document.getElementById('autoModelo').value = item.nombre;
    closeDropdown('modeloDropdown');
    hideNotCatalogued();
    highlightVehicleFound(item);
    updateVehicleInfo();
    if (ns.selections.servicio_id && ns.selections.tipo_vehiculo_id && ns.selections.segmento_id && ns.selections.nivel_suciedad_id) {
      if (window.WizardPricing) window.WizardPricing.fetchPrecio();
    }
  }

  function showNotCatalogued() {
    var el = document.getElementById('notCataloguedMsg');
    if (el) el.style.display = 'block';
    var manual = document.getElementById('manualVehicleType');
    if (manual) manual.style.display = 'block';
    // Re-render tipo/segmento cards as fallback
    if (window.WizardRendering) {
      window.WizardRendering.renderTiposVehiculo();
      window.WizardRendering.renderSegmentos();
    }
    ns.selections.modelo_id = null;
    ns.selections.modelo = (document.getElementById('autoModelo') || {}).value || '';
  }

  function hideNotCatalogued() {
    var el = document.getElementById('notCataloguedMsg');
    if (el) el.style.display = 'none';
    var manual = document.getElementById('manualVehicleType');
    if (manual) manual.style.display = 'none';
    highlightVehicleFound(null);
  }

  function highlightVehicleFound(item) {
    var el = document.getElementById('vehicleFoundInfo');
    if (!el) return;
    if (item) {
      el.style.display = 'block';
      el.innerHTML =
        '<div class="ead-alert ead-alert-success">' +
        '<i class="fa-solid fa-circle-check me-2"></i>' +
        '<strong>' + H.escapeHtml(item.marca_nombre + ' ' + item.nombre) + '</strong> encontrado en el catalogo.' +
        '<div class="mt-1 small" style="opacity:0.8">' +
        'Tipo: <span style="font-weight:700">' + H.escapeHtml(item.tipo_vehiculo_nombre || '') + '</span> | ' +
        'Segmento: <span style="font-weight:700">' + H.escapeHtml(item.segmento_nombre || '') + '</span>' +
        '</div></div>';
      if (window.WizardRendering) {
        window.WizardRendering.highlightTipoSegmento(item.tipo_vehiculo_id, item.segmento_id);
      }
    } else {
      el.style.display = 'none';
      el.innerHTML = '';
    }
  }

  function updateVehicleInfo() {
    if (window.WizardSummary) window.WizardSummary.renderResumen();
  }

  function renderDropdown(dropId, inputId, items, labelKey, onSelect, subtitleFn) {
    closeDropdown(dropId);
    var inp = document.getElementById(inputId);
    if (!inp || !items.length) return;

    var wrapper = inp.closest('.ead-autocomplete-wrapper') || inp.parentElement;
    var dd = document.createElement('div');
    dd.id = dropId;
    dd.className = 'ead-autocomplete-dropdown';
    // Ensure wrapper is positioned
    wrapper.style.position = 'relative';

    var html = '';
    items.forEach(function (item) {
      var sub = subtitleFn ? subtitleFn(item) : '';
      html += '<div class="ead-autocomplete-item" data-id="' + item.id + '">' +
        '<span>' + H.escapeHtml(item[labelKey]) + '</span>' + sub + '</div>';
    });
    dd.innerHTML = html;
    wrapper.appendChild(dd);

    dd.querySelectorAll('.ead-autocomplete-item').forEach(function (div) {
      div.addEventListener('click', function () {
        var item = items.find(function (x) { return x.id === parseInt(div.dataset.id); });
        if (item) onSelect(item);
      });
    });
  }

  function closeDropdown(id) {
    var dd = document.getElementById(id);
    if (dd) dd.remove();
  }

  window.WizardVehiculoAutocomplete = {
    init: init,
    searchModelos: searchModelos,
    selectMarca: selectMarca,
    closeDropdown: closeDropdown,
  };
})();
