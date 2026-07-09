(function () {
  'use strict';

  var ns = window.WizardState;
  var V = window.WizardValidations;
  var R = window.WizardRendering;
  var P = window.WizardPricing;
  var A = window.WizardAvailability;
  var S = window.WizardSummary;

  function goStep(n) {
    if (n < 1 || n > ns.totalSteps) return;
    if (n > ns.maxStepReached + 1) return;

    ns.currentStep = n;
    if (n > ns.maxStepReached) ns.maxStepReached = n;

    // Fade transition
    document.querySelectorAll('.ead-step-pane').forEach(function (p) {
      p.style.opacity = '0';
      p.style.transform = 'translateY(6px)';
      setTimeout(function () { p.classList.add('d-none'); }, 240);
    });

    setTimeout(function () {
      var pane = document.getElementById('paso-' + n);
      if (pane) {
        pane.classList.remove('d-none');
        requestAnimationFrame(function () {
          pane.style.opacity = '1';
          pane.style.transform = 'translateY(0)';
        });
      }
    }, 250);
    // ────────────────────────

    document.querySelectorAll('.ead-step-indicator').forEach(function (s, i) {
      s.classList.remove('active', 'completed');
      s.removeAttribute('data-clickable');
      s.setAttribute('aria-selected', 'false');
      if (i + 1 < n) { s.classList.add('completed'); s.setAttribute('data-clickable', 'true'); s.setAttribute('aria-selected', 'true'); }
      if (i + 1 === n) { s.classList.add('active'); s.setAttribute('aria-selected', 'true'); }
    });

    updateProgress();
    updateMobileProgress(n);

    var sidebar = document.getElementById('wizardSidebar');
    if (sidebar) { sidebar.style.display = window.innerWidth < 768 ? 'none' : ''; }

    // ─── 5-step initializations ───
    if (n === 1) {
      R.renderServiciosBase();
      R.renderPaquetes();
      R.renderPaqueteComposicion(null);
      R.renderInspeccionAviso(null);
      // Restore detail panel if service was already picked
      if (ns.selections.servicio_id) {
        R.showServicioDetalle(ns.selections.servicio_id);
      }
    }
    if (n === 2) {
      R.renderTiposVehiculo();
      R.renderSegmentos();
      if (ns.selections.modelo_id) {
        var fi = document.getElementById('vehicleFoundInfo');
        if (fi) fi.style.display = 'block';
        var mt = document.getElementById('manualVehicleType');
        if (mt) mt.style.display = 'none';
        var nm = document.getElementById('notCataloguedMsg');
        if (nm) nm.style.display = 'none';
        R.highlightTipoSegmento(ns.selections.tipo_vehiculo_id, ns.selections.segmento_id);
      }
    }
    if (n === 3) {
      A.loadSlotsForToday();
      var today = new Date().toISOString().split('T')[0];
      ns.selections.fecha = ns.selections.fecha || today;
      var inp = document.getElementById('inpFecha');
      if (inp && !inp.value) { inp.value = today; inp.min = today; }
    }
    if (n === 5) {
      S.renderStep5Summary();
    }

    S.renderResumen();
    setTimeout(function () { S.renderResumen(); }, 60);
  }

  function nextStep() {
    if (!V.validateStep(ns.currentStep)) return;
    collectFormData();
    if (ns.currentStep < ns.totalSteps) goStep(ns.currentStep + 1);
  }

  function prevStep() {
    collectFormData();
    if (ns.currentStep > 1) goStep(ns.currentStep - 1);
  }

  function updateProgress() {
    var bar = document.getElementById('progressBar');
    if (bar) {
      var pct = Math.round((ns.currentStep / ns.totalSteps) * 100);
      bar.style.width = pct + '%';
      bar.textContent = 'Paso ' + ns.currentStep + ' de ' + ns.totalSteps;
    }
  }

  function updateMobileProgress(n) {
    var lbl = document.getElementById('progressMobileLabel');
    if (lbl) lbl.textContent = 'Paso ' + n + ' de ' + ns.totalSteps;
    var fill = document.getElementById('progressMobileFill');
    if (fill) fill.style.width = Math.round((n / ns.totalSteps) * 100) + '%';
  }

  function collectFormData() {
    var s = ns.selections;
    s.nombre = (document.getElementById('inpNombre') || {}).value || '';
    s.apellido = (document.getElementById('inpApellido') || {}).value || '';
    s.telefono = (document.getElementById('inpTelefono') || {}).value || '';
    s.cedula = (document.getElementById('inpCedula') || {}).value || '';
    s.email = (document.getElementById('inpEmail') || {}).value || '';
    s.color = (document.getElementById('inpColor') || {}).value || '';
    s.chapa = (document.getElementById('inpChapa') || {}).value || '';
    s.anio = parseInt((document.getElementById('inpAnio') || {}).value) || null;
    s.combustible = (document.getElementById('inpCombustible') || {}).value || '';
    s.transmision = (document.getElementById('inpTransmision') || {}).value || '';
    var marcaInput = (document.getElementById('autoMarca') || {}).value || '';
    var modeloInput = (document.getElementById('autoModelo') || {}).value || '';
    s.marca = marcaInput;
    s.modelo = modeloInput;
    var fechaVal = (document.getElementById('inpFecha') || {}).value;
    if (fechaVal) ns.selections.fecha = fechaVal;
  }

  window.WizardNavigation = {
    goStep: goStep,
    nextStep: nextStep,
    prevStep: prevStep,
    updateProgress: updateProgress,
    collectFormData: collectFormData,
  };
})();
