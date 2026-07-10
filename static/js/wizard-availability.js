(function () {
  'use strict';

  var ns = window.WizardState;
  var API = window.WizardAPI;

  function loadSlots(fecha) {
    var container = document.getElementById('slotsContainer');
    if (!container) return;
    container.innerHTML = '<div class="text-center py-2"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><p class="mt-1 mb-0 text-muted small">Cargando horarios...</p></div>';

    API.fetchHorarios(fecha, ns.selections.tipo_vehiculo_id, ns.duracion).then(function (data) {
      if (!data.success) {
        container.innerHTML = '<p class="text-danger">' + (data.error || 'No hay disponibilidad') + '</p>';
        return;
      }
      renderSlots(data);
    }).catch(function () {
      container.innerHTML = '<p class="text-danger">Error al cargar horarios.</p>';
    });
  }

  function loadSlotsForToday() {
    var today = new Date().toISOString().split('T')[0];
    ns.selections.fecha = today;
    resetDateChips(0);
    loadSlots(today);
  }

  function renderSlots(data) {
    var container = document.getElementById('slotsContainer');
    if (!container) return;
    var slots = data.slots || [];
    if (!slots.length) {
      container.innerHTML = '<p class="text-warning">No hay horarios disponibles para este dia.</p>';
      return;
    }

    var selected = ns.selections.hora_inicio;
    var firstAvailable = null;
    var availableCount = 0;

    slots.forEach(function (s) { if (s.disponible) { availableCount++; if (!firstAvailable) firstAvailable = s.hora; } });

    // Preselect first available if nothing selected yet
    if (!selected && firstAvailable) {
      selected = firstAvailable;
      ns.selections.hora_inicio = firstAvailable;
    }

    // Best slot banner
    var banner = document.getElementById('bestSlotBanner');
    if (banner && firstAvailable && !ns.selections.hora_inicio) {
      banner.style.display = 'block';
      banner.innerHTML = '<div class="p-2 rounded" style="background:var(--color-success-tint);border:1px solid rgba(47,183,104,0.3);">' +
        '<i class="fa-solid fa-bolt text-success me-2"></i>' +
        '<strong>Proximo turno disponible:</strong> ' + firstAvailable + ' hs' +
        (availableCount <= 2 ? ' <span style="color:var(--color-warning);font-size:var(--text-caption);">(quedan ' + availableCount + ' turnos)</span>' : '') +
        '</div>';
    } else if (banner) {
      banner.style.display = 'none';
    }

    var html = '<div class="row g-1">';
    slots.forEach(function (slot) {
      var cls = 'ead-time-slot';
      if (!slot.disponible) cls += ' ead-slot-ocupado';
      if (selected === slot.hora) cls += ' selected';
      var onclick = slot.disponible
        ? ' onclick="window.WizardAvailability.selectSlot(this)"'
        : ' title="No disponible"';
      html += '<div class="col-4 col-sm-3 col-md-2"><div class="' + cls + '" data-value="' + slot.hora + '"' + onclick + '>' +
        slot.hora + '</div></div>';
    });
    html += '</div>';
    container.innerHTML = html;

    if (window.WizardSummary) window.WizardSummary.renderResumen();
  }

  // ─── DATE QUICK CHIPS ───
  function selectQuickDate(offset) {
    resetDateChips(offset);

    var pickerWrap = document.getElementById('datePickerWrap');
    var inp = document.getElementById('inpFecha');

    if (offset === 'custom') {
      // Toggle date picker visibility
      if (pickerWrap) {
        var vis = pickerWrap.style.display === 'block';
        pickerWrap.style.display = vis ? 'none' : 'block';
        if (!vis && inp) inp.focus();
      }
      return;
    }

    // Hide custom picker
    if (pickerWrap) pickerWrap.style.display = 'none';

    var d = new Date();
    d.setDate(d.getDate() + offset);
    var fecha = d.toISOString().split('T')[0];

    ns.selections.fecha = fecha;
    ns.selections.hora_inicio = null;
    if (inp) inp.value = fecha;
    loadSlots(fecha);
  }

  function resetDateChips(activeOffset) {
    document.querySelectorAll('.date-chip').forEach(function (chip) {
      chip.classList.remove('active');
      if (parseInt(chip.dataset.offset) === activeOffset) chip.classList.add('active');
    });
    // If custom, mark the picker chip
    if (activeOffset === 'custom') {
      var picker = document.querySelector('.date-chip-picker');
      if (picker) picker.classList.add('active');
    }
  }

  function toggleDatePicker() {
    selectQuickDate('custom');
  }

  window.WizardAvailability = {
    loadSlots: loadSlots,
    loadSlotsForToday: loadSlotsForToday,
    selectSlot: function (el) {
      if (el.classList.contains('ead-slot-ocupado')) return;
      var slots = document.querySelectorAll('.ead-time-slot');
      slots.forEach(function (s) { s.classList.remove('selected'); });
      el.classList.add('selected');
      ns.selections.hora_inicio = el.dataset.value;
      if (window.WizardSummary) window.WizardSummary.renderResumen();
    },
    selectQuickDate: selectQuickDate,
    toggleDatePicker: toggleDatePicker,
  };
})();
