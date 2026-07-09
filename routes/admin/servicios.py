from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from decorators import role_required
from models.servicio import Servicio
from models.categoria_servicio import CategoriaServicio
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache


@admin_bp.route('/servicios')
@login_required
@role_required('admin')
def listar_servicios():
    lista = Servicio.query.filter_by(deleted_at=None).order_by(
        Servicio.tipo, Servicio.nombre
    ).all()
    categorias = CategoriaServicio.query.order_by(CategoriaServicio.orden).all()
    return render_template(
        'admin/servicios.html',
        servicios=lista,
        categorias=categorias,
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

    from re import sub
    slug = sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')

    servicio = Servicio(
        nombre=nombre,
        slug=slug,
        descripcion=data.get('descripcion', ''),
        tipo=data.get('tipo', 'base'),
        categoria_servicio_id=int(data.get('categoria_servicio_id', 1)),
        requiere_inspeccion_previa=data.get('requiere_inspeccion_previa') == '1',
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
    servicio.tipo = data.get('tipo', servicio.tipo)
    servicio.categoria_servicio_id = int(data.get('categoria_servicio_id', servicio.categoria_servicio_id))
    servicio.requiere_inspeccion_previa = data.get('requiere_inspeccion_previa') == '1'
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
