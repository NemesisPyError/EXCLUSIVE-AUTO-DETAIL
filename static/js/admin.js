(function () {
    'use strict';

    // =============================================
    // CSRF helper
    // =============================================
    function csrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.content : '';
    }

    function csrfHeaders(extra) {
        var h = { 'X-CSRFToken': csrfToken() };
        for (var k in extra) { h[k] = extra[k]; }
        return h;
    }

    // =============================================
    // INIT — Bootstrap tooltips
    // =============================================
    document.addEventListener('DOMContentLoaded', function () {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    });

    // =============================================
    // TOGGLE ACTIVO/INACTIVO — Horarios
    // =============================================
    document.addEventListener('change', function (e) {
        if (e.target.matches('.toggle-horario')) {
            var id = e.target.dataset.id;
            fetch('/admin/horarios/' + id + '/toggle', {
                method: 'POST',
                headers: csrfHeaders({})
            })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.success) {
                        showToast(data.mensaje || 'Estado cambiado', 'success');
                        setTimeout(function () { location.reload(); }, 300);
                    } else {
                        showToast(data.error || 'Error', 'danger');
                    }
                })
                .catch(function () { showToast('Error de conexión', 'danger'); });
        }
    });

    // =============================================
    // TOAST NOTIFICATION
    // =============================================
    function showToast(message, type) {
        var container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;max-width:400px;';
            document.body.appendChild(container);
        }

        var toast = document.createElement('div');
        var bgColor = type === 'success'
            ? 'background:rgba(25,135,84,0.2);border:1px solid rgba(25,135,84,0.3);color:#9bddb0;'
            : type === 'danger'
            ? 'background:rgba(220,53,69,0.2);border:1px solid rgba(220,53,69,0.3);color:#f5a3a3;'
            : 'background:rgba(13,202,240,0.2);border:1px solid rgba(13,202,240,0.3);color:#9eeaf9;';
        toast.style.cssText = bgColor + 'padding:0.75rem 1.25rem;border-radius:8px;font-size:0.85rem;animation:toastIn 0.3s ease;font-family:Montserrat,sans-serif;';
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s ease';
            setTimeout(function () { toast.remove(); }, 300);
        }, 4000);
    }

    // Inject keyframes for toast
    var style = document.createElement('style');
    style.textContent = '@keyframes toastIn { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:translateX(0); } }';
    document.head.appendChild(style);

})();
