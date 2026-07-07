from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from decorators import role_required
from models.servicio import Servicio, CategoriaServicioEnum
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache


@admin_bp.route('/servicios')
@login_required
@role_required('admin')
def listar_servicios():
    lista = Servicio.query.order_by(Servicio.categoria, Servicio.nombre).all()
    categorias = CategoriaServicioEnum
    return render_template(
        'admin/servicios.html',
        servicios=lista,
        categorias=[c.value for c in categorias],
    )


@admin_bp.route('/servicios/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_servicio():
    data = request.form
    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre del servicio es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_servicios'))

    servicio = Servicio(
        nombre=nombre,
        descripcion=data.get('descripcion', ''),
        categoria=data.get('categoria', 'lavado_vehiculo'),
        precio=0.0 if data.get('gratis') == '1' else float(data.get('precio') or 0),
        tiempo_estimado_min=int(data.get('tiempo_horas') or 0) * 60 + int(data.get('tiempo_minutos') or 0),
        activo=data.get('activo', '1') == '1',
    )
    db.session.add(servicio)
    db.session.commit()
    _invalidar_cache()
    flash('Servicio creado correctamente.', 'success')
    return redirect(url_for('admin.listar_servicios'))


@admin_bp.route('/servicios/<int:servicio_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    data = request.form

    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre del servicio es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_servicios'))

    servicio.nombre = nombre
    servicio.descripcion = data.get('descripcion', '')
    servicio.categoria = data.get('categoria', servicio.categoria)
    servicio.precio = 0.0 if data.get('gratis') == '1' else float(data.get('precio') or 0)
    servicio.tiempo_estimado_min = int(data.get('tiempo_horas') or 0) * 60 + int(data.get('tiempo_minutos') or 0)
    servicio.activo = data.get('activo', '1') == '1'
    db.session.commit()
    _invalidar_cache()
    flash('Servicio actualizado correctamente.', 'success')
    return redirect(url_for('admin.listar_servicios'))


@admin_bp.route('/servicios/<int:servicio_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    try:
        servicio.activo = False
        db.session.commit()
        _invalidar_cache()
        flash('Servicio desactivado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error('/admin/servicios/eliminar', str(e))
        flash('Error al desactivar el servicio.', 'danger')
    return redirect(url_for('admin.listar_servicios'))
