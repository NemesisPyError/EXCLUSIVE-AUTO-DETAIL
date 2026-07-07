from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.usuario import Usuario
from extensions import db, limiter
from services.security_service import (
    log_login_success, log_login_failed, log_login_locked, log_logout,
    log_reset_token_sent, log_password_reset
)
from services.email_service import send_password_reset
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message='Demasiados intentos de inicio de sesión. Intente de nuevo en un minuto.')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Complete todos los campos.', 'danger')
            return render_template('login.html')

        user = Usuario.query.filter_by(email=email).first()

        if user is None:
            log_login_failed(email)
            flash('Email o contrasena incorrectos.', 'danger')
            return render_template('login.html')

        if not user.activo:
            log_login_failed(email)
            flash('Cuenta desactivada. Contacte al administrador.', 'danger')
            return render_template('login.html')

        user.unlock_if_expired()

        if user.is_locked:
            log_login_locked(email)
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60
            flash(
                f'Cuenta bloqueada por intentos fallidos. '
                f'Intente de nuevo en {remaining} minuto(s).',
                'danger'
            )
            return render_template('login.html')

        if not user.check_password(password):
            user.record_failed_attempt()
            db.session.commit()
            log_login_failed(email)
            intentos_restantes = max(0, user.MAX_LOGIN_ATTEMPTS - user.login_attempts)
            if intentos_restantes == 0:
                flash(
                    'Cuenta bloqueada por exceso de intentos fallidos. '
                    'Intente de nuevo en 15 minutos.',
                    'danger'
                )
            else:
                flash(
                    f'Email o contraseña incorrectos. '
                    f'Intentos restantes: {intentos_restantes}.',
                    'danger'
                )
            return render_template('login.html')

        user.reset_login_attempts()
        db.session.commit()

        login_user(user, remember=False)
        session['_session_version'] = user.session_version
        log_login_success(email)
        flash(f'Bienvenido, {user.nombre}.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_logout(current_user.email)
    logout_user()
    session.clear()
    flash('Sesion cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message='Demasiadas solicitudes. Intente en un minuto.')
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Ingrese una direccion de correo electronico.', 'danger')
            return render_template('forgot_password.html')

        user = Usuario.query.filter_by(email=email).first()

        if user and user.activo:
            user.unlock_if_expired()

        if user and user.activo and not user.is_locked:
            user.generate_reset_token()
            db.session.commit()
            log_reset_token_sent(email)
            reset_url = url_for('auth.reset_password',
                                token=user.reset_token, _external=True)
            current_app.logger.info(
                f'PASSWORD RESET LINK para {email}: {reset_url}'
            )
            smtp_ok = send_password_reset(email, reset_url)
            current_app.logger.info(
                f'SMTP password reset to {email}: {"OK" if smtp_ok else "FAILED"}'
            )

        flash(
            'Si el correo esta registrado, recibira instrucciones para '
            'restablecer su contrasena.',
            'info'
        )
        return render_template('forgot_password.html')

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if not token or len(token) < 10:
        flash('Enlace de recuperacion invalido.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = Usuario.query.filter_by(reset_token=token).first()
    if not user or not user.activo:
        flash('Enlace de recuperacion invalido o expirado.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if user.reset_token_expiry and user.reset_token_expiry < datetime.utcnow():
        user.clear_reset_token()
        db.session.commit()
        flash('El enlace de recuperacion ha expirado. Solicite uno nuevo.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not password or not confirm:
            flash('Complete todos los campos.', 'danger')
            return render_template('reset_password.html', token=token)

        if len(password) < 8:
            flash('La contrasena debe tener al menos 8 caracteres.', 'danger')
            return render_template('reset_password.html', token=token)

        if password != confirm:
            flash('Las contrasenas no coinciden.', 'danger')
            return render_template('reset_password.html', token=token)

        user.set_password(password)
        user.increment_session_version()
        user.clear_reset_token()
        user.reset_login_attempts()
        db.session.commit()

        log_password_reset(user.email)
        flash('Contrasena restablecida correctamente. Inicie sesion.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
