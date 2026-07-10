(function () {
  'use strict';

  var ns = window.WizardState;
  var API = window.WizardAPI;

  var MARGEN_TALLER = 15;
  var controller = null;

  function fetchPrecio() {
    var s = ns.selections;
    if (!s.servicio_id || !s.tipo_vehiculo_id || !s.segmento_id || !s.nivel_suciedad_id) return;

    var cacheKey = s.servicio_id + '/' + s.tipo_vehiculo_id + '/' + s.segmento_id + '/' + s.nivel_suciedad_id;
    if (ns.preciosCache[cacheKey]) {
      aplicarPrecio();
      return;
    }

    if (controller) controller.abort();
    controller = new AbortController();

    API.fetchPrecio(s.servicio_id, s.tipo_vehiculo_id, s.segmento_id, s.nivel_suciedad_id)
      .then(function (data) {
        if (data.success && data.precio) {
          ns.preciosCache[cacheKey] = data.precio;
          aplicarPrecio();
        }
      })
      .catch(function () {});
  }

  function fetchPrecioAdicional(adId, callback) {
    var s = ns.selections;
    var cacheKey = adId + '/' + s.tipo_vehiculo_id + '/' + s.segmento_id + '/' + s.nivel_suciedad_id;
    if (ns.preciosCache[cacheKey]) {
      if (callback) callback(ns.preciosCache[cacheKey]);
      return;
    }
    API.fetchPrecio(adId, s.tipo_vehiculo_id, s.segmento_id, s.nivel_suciedad_id)
      .then(function (data) {
        if (data.success && data.precio) {
          ns.preciosCache[cacheKey] = data.precio;
          if (callback) callback(data.precio);
        }
      })
      .catch(function () {});
  }

  function aplicarPrecio() {
    var s = ns.selections;
    var cacheKey = s.servicio_id + '/' + s.tipo_vehiculo_id + '/' + s.segmento_id + '/' + s.nivel_suciedad_id;
    var base = ns.preciosCache[cacheKey];
    if (!base) return;

    ns.precio = Object.assign({}, base);
    ns.duracion = (base.duracion_minutos || 60) + MARGEN_TALLER;

    var adicionalesIds = ns.selections.adicionales_ids || [];
    var pending = adicionalesIds.length;

    if (pending === 0) {
      renderAll();
      return;
    }

    adicionalesIds.forEach(function (adId) {
      fetchPrecioAdicional(adId, function (adPrice) {
        ns.precio.precio += adPrice.precio || 0;
        ns.duracion += adPrice.duracion_minutos || 0;
        pending--;
        if (pending === 0) renderAll();
      });
    });
  }

  function renderAll() {
    if (window.WizardRendering) window.WizardRendering.renderPrecioBadge();
    if (window.WizardSummary) window.WizardSummary.renderResumen();
    if (ns.currentStep === 3 && ns.selections.fecha && ns.selections.tipo_vehiculo_id) {
      if (window.WizardAvailability) window.WizardAvailability.loadSlots(ns.selections.fecha);
    }
  }

  window.WizardPricing = {
    fetchPrecio: fetchPrecio,
    updatePrecio: function () { fetchPrecio(); },
  };
})();
