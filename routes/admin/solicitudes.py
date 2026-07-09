from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.solicitud_catalogo import SolicitudCatalogo
from models.marca import Marca
from models.modelo_vehiculo import ModeloVehiculo
from models.vehiculo import Vehiculo
from services.security_service import log_admin_action, log_error
from routes.admin import admin_bp, _invalidar_cache
import re


@admin_bp.route('/solicitudes-catalogo')
@login_required
@role_required('admin')
def listar_solicitudes():
    filtro = request.args.get('estado', 'pendiente').strip()
    page = request.args.get('page', 1, type=int)

    from sqlalchemy.orm import joinedload
    query = SolicitudCatalogo.query.options(
        joinedload(SolicitudCatalogo.tipo_vehiculo),
        joinedload(SolicitudCatalogo.segmento),
        joinedload(SolicitudCatalogo.cliente),
        joinedload(SolicitudCatalogo.marca),
    )

    if filtro and filtro in ('pendiente', 'aprobada', 'rechazada'):
        query = query.filter(SolicitudCatalogo.estado == filtro)

    query = query.order_by(SolicitudCatalogo.created_at.desc())
    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    return render_template(
        'admin/solicitudes.html',
        solicitudes=paginacion.items,
        paginacion=paginacion,
        filtro_estado=filtro,
    )


@admin_bp.route('/solicitudes-catalogo/<int:solicitud_id>/aprobar', methods=['POST'])
@login_required
@role_required('admin')
def aprobar_solicitud(solicitud_id):
    sol = (
        SolicitudCatalogo.query
        .filter(SolicitudCatalogo.id == solicitud_id)
        .with_for_update()
        .first()
    )
    if not sol:
        flash('Solicitud no encontrada.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))

    if sol.estado != 'pendiente':
        flash('Esta solicitud ya fue procesada.', 'warning')
        return redirect(url_for('admin.listar_solicitudes'))

    nombre_marca = (request.form.get('nombre_marca') or sol.marca_texto).strip()
    nombre_modelo = (request.form.get('nombre_modelo') or sol.modelo_texto).strip()

    if not nombre_marca or not nombre_modelo:
        flash('Marca y modelo son obligatorios.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))

    marca_slug = re.sub(r'[^a-z0-9]+', '-', nombre_marca.lower()).strip('-')
    marca = Marca.query.filter_by(slug=marca_slug).first()
    if not marca:
        marca = Marca(
            nombre=nombre_marca,
            slug=marca_slug,
            pais_origen=(request.form.get('pais_origen') or '').strip() or None,
            activo=True,
        )
        db.session.add(marca)
        db.session.flush()

    modelo_slug = re.sub(r'[^a-z0-9]+', '-', nombre_modelo.lower()).strip('-')
    modelo = ModeloVehiculo.query.filter_by(marca_id=marca.id, slug=modelo_slug).first()
    if not modelo:
        modelo = ModeloVehiculo(
            marca_id=marca.id,
            nombre=nombre_modelo,
            slug=modelo_slug,
            tipo_vehiculo_id=sol.tipo_vehiculo_id,
            segmento_id=sol.segmento_id,
            activo=True,
        )
        db.session.add(modelo)
        db.session.flush()

    if sol.vehiculo_id:
        vehiculo = db.session.get(Vehiculo, sol.vehiculo_id)
        if vehiculo:
            vehiculo.marca_id = marca.id
            vehiculo.modelo_id = modelo.id
            vehiculo.tipo_vehiculo_id = sol.tipo_vehiculo_id
            vehiculo.segmento_id = sol.segmento_id

    sol.marca_id = marca.id
    sol.modelo_id = modelo.id
    sol.estado = 'aprobada'
    sol.usuario_aprobador_id = current_user.id
    db.session.commit()

    _invalidar_cache()
    log_admin_action(current_user.email, 'aprobar_solicitud_catalogo', f'Solicitud #{solicitud_id} -> {nombre_marca} {nombre_modelo}')
    flash(f'Solicitud aprobada. Se creo "{nombre_marca} {nombre_modelo}" en el catalogo.', 'success')
    return redirect(url_for('admin.listar_solicitudes'))


@admin_bp.route('/solicitudes-catalogo/<int:solicitud_id>/rechazar', methods=['POST'])
@login_required
@role_required('admin')
def rechazar_solicitud(solicitud_id):
    sol = (
        SolicitudCatalogo.query
        .filter(SolicitudCatalogo.id == solicitud_id)
        .with_for_update()
        .first()
    )
    if not sol:
        flash('Solicitud no encontrada.', 'danger')
        return redirect(url_for('admin.listar_solicitudes'))

    if sol.estado != 'pendiente':
        flash('Esta solicitud ya fue procesada.', 'warning')
        return redirect(url_for('admin.listar_solicitudes'))

    sol.estado = 'rechazada'
    sol.usuario_aprobador_id = current_user.id
    sol.observaciones = (request.form.get('observaciones') or '').strip() or None
    db.session.commit()
    log_admin_action(current_user.email, 'rechazar_solicitud_catalogo', f'Solicitud #{solicitud_id}')
    flash('Solicitud rechazada.', 'info')
    return redirect(url_for('admin.listar_solicitudes'))
