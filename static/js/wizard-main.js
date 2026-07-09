(function () {
  'use strict';

  var ns = window.WizardState;
  var N = window.WizardNavigation;
  var API = window.WizardAPI;
  var R = window.WizardRendering;
  var P = window.WizardPricing;
  var A = window.WizardAvailability;
  var S = window.WizardSummary;
  var V = window.WizardValidations;

  function hideLoading(id) {
    var el = document.getElementById(id);
    if (el) el.style.display = 'none';
  }

  function init() {
    API.fetchServicios('base').then(function (data) {
      if (data.success) { ns.servicios.base = data.servicios || []; }
    }).finally(function () { hideLoading('serviciosLoading'); });

    API.fetchServicios('adicional').then(function (data) {
      if (data.success) { ns.servicios.adicional = data.servicios || []; }
    });

    API.fetchServicios('paquete').then(function (data) {
      if (data.success) { ns.servicios.paquete = data.servicios || []; R.renderPaquetes(); }
    }).finally(function () { hideLoading('paquetesLoading'); });

    API.fetchNivelesSuciedad().then(function (data) {
      if (data.success) { ns.nivelesSuciedad = data.niveles || []; }
    });

    API.fetchTiposVehiculo().then(function (data) {
      if (data.success) { ns.tiposVehiculo = data.tipos_vehiculo || []; }
    }).finally(function () { hideLoading('tiposVehiculoLoading'); });

    API.fetchSegmentos().then(function (data) {
      if (data.success) { ns.segmentos = data.segmentos || []; }
    }).finally(function () { hideLoading('segmentosLoading'); });

    R.renderServiciosBase();
    bindButtons();
    bindDatePicker();
    document.getElementById('inpFecha').addEventListener('change', function () {
      ns.selections.fecha = this.value;
      A.loadSlots(this.value);
      S.renderResumen();
    });
    if (window.WizardVehiculoAutocomplete) window.WizardVehiculoAutocomplete.init();
  }

  function bindButtons() {
    ['btnNext', 'btnNext2', 'btnNext3', 'btnNext4'].forEach(function (id) {
      var b = document.getElementById(id);
      if (b) b.addEventListener('click', function () { N.nextStep(); });
    });
    ['btnPrev', 'btnPrev2', 'btnPrev3', 'btnPrev4', 'btnPrev5'].forEach(function (id) {
      var b = document.getElementById(id);
      if (b) b.addEventListener('click', function () { N.prevStep(); });
    });

    document.querySelectorAll('.ead-step-indicator').forEach(function (step) {
      step.addEventListener('click', function () {
        if (this.hasAttribute('data-clickable')) {
          var targetStep = parseInt(this.getAttribute('data-step'));
          if (targetStep) N.goStep(targetStep);
        }
      });
    });
  }

  function bindDatePicker() {
    var inp = document.getElementById('inpFecha');
    if (inp) {
      var today = new Date().toISOString().split('T')[0];
      if (!inp.value) { inp.value = today; ns.selections.fecha = today; inp.min = today; }
    }
  }

  function toggleOptionalFields() {
    var el = document.getElementById('optionalFields');
    var btn = document.getElementById('btnMoreInfo');
    if (!el || !btn) return;
    var hidden = el.style.display === 'none' || !el.style.display;
    el.style.display = hidden ? 'flex' : 'none';
    btn.classList.toggle('expanded', hidden);
    btn.innerHTML = hidden ?
      '<i class="fa-solid fa-chevron-up me-1"></i>Menos informacion' :
      '<i class="fa-solid fa-chevron-down me-1"></i>Mas informacion (opcional)';
  }

  function toggleOptionalFieldsP4() {
    var el = document.getElementById('optionalFieldsP4');
    var btn = document.getElementById('btnMoreInfoP4');
    if (!el || !btn) return;
    var hidden = el.style.display === 'none' || !el.style.display;
    el.style.display = hidden ? 'flex' : 'none';
    btn.classList.toggle('expanded', hidden);
    btn.innerHTML = hidden ?
      '<i class="fa-solid fa-chevron-up me-1"></i>Menos informacion' :
      '<i class="fa-solid fa-chevron-down me-1"></i>Informacion adicional (opcional)';
  }

  window.WizardMain = {
    init: init,
    toggleOptionalFields: toggleOptionalFields,
    toggleOptionalFieldsP4: toggleOptionalFieldsP4,
    submit: function () {
      if (ns.submitting) return;
      var btn = document.getElementById('btnSubmit');
      var txt = document.getElementById('btnSubmitText');
      var spin = document.getElementById('btnSubmitSpinner');
      ns.submitting = true;
      if (btn) btn.disabled = true;
      if (txt) txt.textContent = 'Enviando...';
      if (spin) spin.classList.remove('d-none');

      N.collectFormData();
      var payload = buildPayload();

      API.submitReserva(payload).then(function (data) {
        if (data.success && data.confirmacion_token) {
          window.location.href = '/reservas/confirmacion/' + data.confirmacion_token;
        } else {
          ns.submitting = false;
          if (btn) btn.disabled = false;
          if (txt) txt.textContent = 'Confirmar Reserva';
          if (spin) spin.classList.add('d-none');
          var err = data.error || (data.errors ? JSON.stringify(data.errors) : 'Error al crear la reserva.');
          V.showBanner(err);
        }
      }).catch(function () {
        ns.submitting = false;
        if (btn) btn.disabled = false;
        if (txt) txt.textContent = 'Confirmar Reserva';
        if (spin) spin.classList.add('d-none');
        V.showBanner('Error de conexion. Intenta de nuevo.');
      });
    },
  };

  function buildPayload() {
    var s = ns.selections;
    var marcaInput = (document.getElementById('autoMarca') || {}).value || '';
    var modeloInput = (document.getElementById('autoModelo') || {}).value || '';

    return {
      tipo_vehiculo_id: s.tipo_vehiculo_id,
      segmento_id: s.segmento_id,
      servicio_id: s.servicio_id,
      nivel_suciedad_id: s.nivel_suciedad_id,
      adicionales_ids: s.adicionales_ids || [],
      fecha: s.fecha,
      hora_inicio: s.hora_inicio,
      nombre: s.nombre,
      apellido: s.apellido,
      telefono: s.telefono,
      cedula: s.cedula || '',
      email: s.email || '',
      marca: marcaInput,
      modelo: modeloInput,
      modelo_id: s.modelo_id || null,
      marca_id: s.marca_id || null,
      anio: s.anio,
      color: s.color || '',
      chapa: s.chapa || '',
      combustible: s.combustible || '',
      transmision: s.transmision || '',
      vehiculo_id: s.vehiculo_id || null,
    };
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('wizardContainer')) init();
  });
})();
