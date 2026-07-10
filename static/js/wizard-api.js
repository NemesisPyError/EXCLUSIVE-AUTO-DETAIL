(function () {
  'use strict';

  var BASE = '/api/publica';

  async function safeJson(resp) {
    var data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Error de red');
    return data;
  }

  window.WizardAPI = {
    fetchTiposVehiculo: function () {
      return fetch(BASE + '/tipos-vehiculo').then(function (r) { return r.json(); });
    },
    fetchSegmentos: function () {
      return fetch(BASE + '/segmentos').then(function (r) { return r.json(); });
    },
    fetchServicios: function (tipo) {
      var url = BASE + '/servicios';
      if (tipo) url += '?tipo=' + tipo;
      return fetch(url).then(function (r) { return r.json(); });
    },
    fetchNivelesSuciedad: function () {
      return fetch(BASE + '/niveles-suciedad').then(function (r) { return r.json(); });
    },
    fetchPrecio: function (servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id) {
      var params = new URLSearchParams({
        servicio_id: servicio_id,
        tipo_vehiculo_id: tipo_vehiculo_id,
        segmento_id: segmento_id,
        nivel_suciedad_id: nivel_suciedad_id,
      });
      return fetch(BASE + '/precio?' + params).then(function (r) { return r.json(); });
    },
    fetchHorarios: function (fecha, tipo_vehiculo_id, duracion_min) {
      var params = new URLSearchParams({
        fecha: fecha,
        tipo_vehiculo_id: tipo_vehiculo_id,
        duracion_min: duracion_min || 60,
      });
      return fetch(BASE + '/disponibilidad?' + params).then(function (r) { return r.json(); });
    },
    fetchMarcas: function (q) {
      return fetch(BASE + '/marcas/buscar?q=' + encodeURIComponent(q)).then(function (r) { return r.json(); });
    },
    fetchModelos: function (q, marcaId) {
      var url = BASE + '/modelos/buscar?q=' + encodeURIComponent(q || '');
      if (marcaId) url += '&marca_id=' + marcaId;
      return fetch(url).then(function (r) { return r.json(); });
    },
    submitReserva: function (payload) {
      return fetch('/reservas/crear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then(function (r) { return r.json(); });
    },
  };
})();
