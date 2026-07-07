from flask import request, session
from flask_login import current_user, logout_user


def register_session_check(app):
    @app.before_request
    def _check_session_version():
        if not current_user.is_authenticated:
            return
        try:
            if hasattr(current_user, 'id') and current_user.id:
                sv = session.get('_session_version')
                if sv is not None and sv != current_user.session_version:
                    from services.security_service import log_session_invalidated
                    email = getattr(current_user, 'email', 'unknown')
                    log_session_invalidated(email, 'session_version_mismatch')
                    logout_user()
                    session.clear()
                    if request.is_json or request.content_type == 'application/json':
                        from flask import jsonify
                        return jsonify({'error': 'Su sesion ha sido invalidada.'}), 401
                    from flask import flash, redirect, url_for
                    flash('Su sesion fue invalidada. Inicie sesion nuevamente.', 'warning')
                    return redirect(url_for('auth.login'))
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                'Error al verificar session version para usuario autenticado.'
            )


def register_security_headers(app):
    def _add_security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=(), usb=()'
        )
        # CSP: 'unsafe-inline' es necesario para el wizard de reservas
        # (~746 lineas JS inline en nueva.html) y los modales CRUD del admin
        # (~600 lineas en admin/galeria.html, admin/reservas.html, etc.).
        # Para eliminar unsafe-inline se requiere:
        #   1. Extraer JS del wizard a static/js/wizard.js
        #   2. Extraer JS de modales admin a static/js/admin-crud.js
        #   3. Usar nonces o hashes en los pocos <script> inline restantes
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' https://cdn.jsdelivr.net; "
            "frame-src https://www.google.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        if not app.debug:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains'
            )
        return response

    app.after_request(_add_security_headers)
