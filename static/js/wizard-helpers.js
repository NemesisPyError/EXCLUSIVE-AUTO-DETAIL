(function () {
  'use strict';

  function formatGuarani(n) {
    return 'Gs ' + String(n || 0).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  function formatearDuracion(min) {
    var h = Math.floor(min / 60);
    var m = min % 60;
    if (h > 0 && m > 0) return h + 'h ' + m + 'min';
    if (h > 0) return h + 'h';
    return m + 'min';
  }

  function escapeHtml(str) {
    var d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
  }

  window.WizardHelpers = {
    formatGuarani: formatGuarani,
    formatearDuracion: formatearDuracion,
    escapeHtml: escapeHtml,
  };
})();
