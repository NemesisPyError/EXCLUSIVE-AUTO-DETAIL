(function () {
  'use strict';

  var container = null;
  var activeToasts = [];
  var MAX_VISIBLE = 2;

  function getContainer() {
    if (!container) {
      container = document.createElement('div');
      container.className = 'ead-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  function showToast(message, type) {
    if (!type) type = 'info';
    var c = getContainer();

    // If at max, remove oldest with a smooth crossfade
    if (activeToasts.length >= MAX_VISIBLE) {
      var oldest = activeToasts.shift();
      dismiss(oldest);
    }

    var el = document.createElement('div');
    el.className = 'ead-toast ead-toast-' + type;
    el.innerHTML =
      '<span>' + escapeHtml(message) + '</span>' +
      '<button class="ead-toast-close" aria-label="Cerrar">&times;</button>';

    c.appendChild(el);
    activeToasts.push(el);

    var closeBtn = el.querySelector('.ead-toast-close');
    closeBtn.addEventListener('click', function () {
      dismiss(el);
    });

    var timeout = setTimeout(function () {
      dismiss(el);
    }, 4500);

    el._timeout = timeout;

    return el;
  }

  function dismiss(el) {
    if (el._dismissed) return;
    el._dismissed = true;

    if (el._timeout) clearTimeout(el._timeout);

    el.classList.add('removing');
    var idx = activeToasts.indexOf(el);
    if (idx !== -1) activeToasts.splice(idx, 1);

    setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, 350);
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  window.showToast = showToast;
})();
