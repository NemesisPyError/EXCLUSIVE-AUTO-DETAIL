from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            if current_user.rol not in roles:
                if request.is_json or request.content_type == 'application/json':
                    return jsonify({
                        'success': False,
                        'error': 'No tiene permisos para realizar esta accion.'
                    }), 403
                flash('No tiene permisos para acceder a esta seccion.', 'danger')
                return redirect(url_for('admin.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
