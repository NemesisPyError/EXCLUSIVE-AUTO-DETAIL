from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.usuario import Usuario
from services.security_service import log_admin_action
from routes.admin import admin_bp


@admin_bp.route('/usuarios')
@login_required
@role_required('admin')
def listar_usuarios():
    import json
    rol_filtro = request.args.get('rol', '').strip()

    query = Usuario.query

    if rol_filtro:
        query = query.filter(Usuario.rol == rol_filtro)

    query = query.order_by(Usuario.nombre)
    usuarios = query.all()

    total = Usuario.query.count()
    activos = Usuario.query.filter_by(activo=True).count()
    inactivos = total - activos

    usuarios_data = json.dumps([
        {
            'id': u.id,
            'nombre': u.nombre,
            'email': u.email,
            'rol': u.rol,
            'activo': u.activo,
        }
        for u in usuarios
    ], ensure_ascii=False)

    return render_template(
        'admin/usuarios.html',
        usuarios=usuarios,
        usuarios_data=usuarios_data,
        rol_filtro=rol_filtro,
        total=total,
        activos=activos,
        inactivos=inactivos,
    )


@admin_bp.route('/usuarios/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_usuario():
    nombre = (request.form.get('nombre') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    password = (request.form.get('password') or '').strip()
    rol = (request.form.get('rol') or 'empleado').strip()

    errores = []
    if not nombre:
        errores.append('El nombre es obligatorio.')
    if not email:
        errores.append('El email es obligatorio.')
    elif Usuario.query.filter_by(email=email).first():
        errores.append('El email ya esta registrado.')
    if not password:
        errores.append('La contrasena es obligatoria.')
    elif len(password) < 8:
        errores.append('La contrasena debe tener al menos 8 caracteres.')
    if rol not in ('admin', 'empleado'):
        errores.append('Rol no valido.')

    if errores:
        for e in errores:
            flash(e, 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    usuario = Usuario(nombre=nombre, email=email, rol=rol)
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()

    log_admin_action(current_user.email, 'crear_usuario', f'id={usuario.id} email={usuario.email} rol={usuario.rol}')
    flash(f'Usuario {nombre} creado correctamente.', 'success')
    return redirect(url_for('admin.listar_usuarios'))


@admin_bp.route('/usuarios/<int:usuario_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.form

    nombre = (data.get('nombre') or '').strip()
    email = (data.get('email') or '').strip().lower()
    rol = (data.get('rol') or '').strip()
    activo = data.get('activo') == '1'

    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    existente = Usuario.query.filter(Usuario.email == email, Usuario.id != usuario_id).first()
    if existente:
        flash('El email ya esta en uso por otro usuario.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    if rol not in ('admin', 'empleado'):
        flash('Rol no valido.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    if usuario.id == current_user.id and not activo:
        flash('No puedes desactivar tu propio usuario.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    usuario.nombre = nombre
    usuario.email = email
    usuario.rol = rol
    usuario.activo = activo
    db.session.commit()

    log_admin_action(current_user.email, 'editar_usuario', f'id={usuario.id} nombre={usuario.nombre} rol={usuario.rol} activo={usuario.activo}')
    flash(f'Usuario {nombre} actualizado correctamente.', 'success')
    return redirect(url_for('admin.listar_usuarios'))


@admin_bp.route('/usuarios/<int:usuario_id>/reset-password', methods=['POST'])
@login_required
@role_required('admin')
def reset_password(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    password = (request.form.get('password') or '').strip()

    if len(password) < 8:
        flash('La contrasena debe tener al menos 8 caracteres.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    usuario.set_password(password)
    usuario.increment_session_version()
    db.session.commit()

    log_admin_action(current_user.email, 'reset_password', f'id={usuario.id} email={usuario.email}')
    flash(f'Contrasena de {usuario.nombre} restablecida correctamente.', 'success')
    return redirect(url_for('admin.listar_usuarios'))


@admin_bp.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('admin.listar_usuarios'))

    usuario.activo = False
    db.session.commit()

    log_admin_action(current_user.email, 'desactivar_usuario', f'id={usuario.id} email={usuario.email}')
    flash(f'Usuario {usuario.nombre} desactivado correctamente.', 'success')
    return redirect(url_for('admin.listar_usuarios'))
