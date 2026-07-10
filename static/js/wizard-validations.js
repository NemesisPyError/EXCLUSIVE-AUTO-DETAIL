(function () {
  'use strict';

  var ns = window.WizardState;

  function showFieldError(fieldId, msg) {
    var el = document.getElementById('fieldError_' + fieldId);
    if (el) { el.textContent = msg; el.classList.remove('d-none'); }
  }

  function clearFieldErrors() {
    document.querySelectorAll('.ead-field-error').forEach(function (e) { e.classList.add('d-none'); });
  }

  function hideBanner() {
    // Toasts auto-dismiss — no action needed
  }

  function showBanner(msg) {
    if (typeof showToast === 'function') {
      showToast(msg, 'error');
    }
  }

  function validateStep(step) {
    hideBanner();
    clearFieldErrors();
    var ok = true;
    var s = ns.selections;

    // Step 1 — Service + Suciedad (merged)
    if (step === 1) {
      if (!s.servicio_id) {
        showFieldError('servicio_id', 'Selecciona un servicio.');
        ok = false;
      }
      if (!s.nivel_suciedad_id) {
        showFieldError('nivel_suciedad_id', 'Selecciona el nivel de suciedad.');
        ok = false;
      }
    }

    // Step 2 — Vehicle
    if (step === 2) {
      var marcaInput = (document.getElementById('autoMarca') || {}).value || '';
      var modeloInput = (document.getElementById('autoModelo') || {}).value || '';
      if (!marcaInput) {
        showFieldError('marca', 'Ingresa la marca de tu vehiculo.');
        ok = false;
      }
      if (!modeloInput) {
        showFieldError('modelo', 'Ingresa el modelo de tu vehiculo.');
        ok = false;
      }
      if (!s.modelo_id) {
        if (!s.tipo_vehiculo_id) {
          showFieldError('tipo_vehiculo_id', 'Selecciona el tipo de vehiculo.');
          ok = false;
        }
        if (!s.segmento_id) {
          showFieldError('segmento_id', 'Selecciona el tamano.');
          ok = false;
        }
      }
    }

    // Step 3 — Agenda
    if (step === 3) {
      if (!s.fecha) {
        showFieldError('fecha', 'Selecciona una fecha.');
        ok = false;
      }
      if (!s.hora_inicio) {
        showFieldError('hora_inicio', 'Selecciona un horario.');
        ok = false;
      }
    }

    // Step 4 — Data
    if (step === 4) {
      var nombre = (document.getElementById('inpNombre') || {}).value || '';
      var apellido = (document.getElementById('inpApellido') || {}).value || '';
      var telefono = (document.getElementById('inpTelefono') || {}).value || '';
      if (!nombre) { showFieldError('nombre', 'Ingresa tu nombre.'); ok = false; }
      if (!apellido) { showFieldError('apellido', 'Ingresa tu apellido.'); ok = false; }
      if (!telefono) { showFieldError('telefono', 'Ingresa tu numero de telefono.'); ok = false; }
    }

    if (!ok) showBanner('Completa los campos indicados para continuar.');
    return ok;
  }

  window.WizardValidations = {
    validateStep: validateStep,
    showBanner: showBanner,
    hideBanner: hideBanner,
    showFieldError: showFieldError,
    clearFieldErrors: clearFieldErrors,
  };
})();
