from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.precio_servicio import PrecioServicio
from models.servicio import Servicio
from models.tipo_vehiculo import TipoVehiculo
from models.segmento import Segmento
from models.nivel_suciedad import NivelSuciedad
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache


@admin_bp.route('/precios')
@login_required
@role_required('admin')
def listar_precios():
    servicio_id = request.args.get('servicio_id', type=int)
    tipo_vehiculo_id = request.args.get('tipo_vehiculo_id', type=int)

    servicios = (
        Servicio.query
        .filter(Servicio.tipo.in_(['base', 'adicional', 'paquete']), Servicio.activo == True, Servicio.deleted_at == None)
        .order_by(Servicio.tipo, Servicio.nombre)
        .all()
    )
    tipos_vehiculo = TipoVehiculo.query.order_by(TipoVehiculo.orden).all()
    segmentos = Segmento.query.order_by(Segmento.orden).all()
    niveles = NivelSuciedad.query.order_by(NivelSuciedad.orden).all()

    precios_data = {}
    precio_objects = {}

    if servicio_id:
        query = PrecioServicio.query.filter_by(servicio_id=servicio_id)
        if tipo_vehiculo_id:
            query = query.filter_by(tipo_vehiculo_id=tipo_vehiculo_id)
        precios = query.all()
        for p in precios:
            key = f'{p.tipo_vehiculo_id}:{p.segmento_id}:{p.nivel_suciedad_id}'
            precios_data[key] = {'precio': p.precio, 'duracion_minutos': p.duracion_minutos}
            precio_objects[key] = p.id

    return render_template(
        'admin/precios.html',
        servicios=servicios,
        tipos_vehiculo=tipos_vehiculo,
        segmentos=segmentos,
        niveles=niveles,
        servicio_id=servicio_id,
        tipo_vehiculo_id=tipo_vehiculo_id,
        precios_data=precios_data,
        precio_objects=precio_objects,
    )


@admin_bp.route('/precios/guardar', methods=['POST'])
@login_required
@role_required('admin')
def guardar_precio():
    precio_id = request.form.get('precio_id', type=int)
    servicio_id = request.form.get('servicio_id', type=int)
    tipo_vehiculo_id = request.form.get('tipo_vehiculo_id', type=int)
    segmento_id = request.form.get('segmento_id', type=int)
    nivel_suciedad_id = request.form.get('nivel_suciedad_id', type=int)
    precio_val = request.form.get('precio', type=int)
    duracion_val = request.form.get('duracion_minutos', type=int)

    if not all([servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id]):
        flash('Todos los campos son obligatorios.', 'danger')
        return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))

    if precio_val is None or precio_val < 0:
        flash('El precio debe ser mayor o igual a 0.', 'danger')
        return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))

    if duracion_val is None or duracion_val <= 0:
        flash('La duracion debe ser mayor a 0 minutos.', 'danger')
        return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))

    if precio_id:
        regla = db.session.get(PrecioServicio, precio_id)
        if not regla:
            flash('Regla no encontrada.', 'danger')
            return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))
        regla.precio = precio_val
        regla.duracion_minutos = duracion_val
        db.session.commit()
    else:
        existente = PrecioServicio.query.filter_by(
            servicio_id=servicio_id,
            tipo_vehiculo_id=tipo_vehiculo_id,
            segmento_id=segmento_id,
            nivel_suciedad_id=nivel_suciedad_id,
        ).first()
        if existente:
            flash('Ya existe una regla para esta combinacion.', 'danger')
            return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))

        db.session.add(PrecioServicio(
            servicio_id=servicio_id,
            tipo_vehiculo_id=tipo_vehiculo_id,
            segmento_id=segmento_id,
            nivel_suciedad_id=nivel_suciedad_id,
            precio=precio_val,
            duracion_minutos=duracion_val,
        ))
        db.session.commit()

    _invalidar_cache()
    flash('Regla guardada correctamente.', 'success')
    return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))


@admin_bp.route('/precios/<int:precio_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_precio(precio_id):
    regla = db.session.get(PrecioServicio, precio_id)
    if not regla:
        flash('Regla no encontrada.', 'danger')
        return redirect(url_for('admin.listar_precios'))
    servicio_id = regla.servicio_id
    db.session.delete(regla)
    db.session.commit()
    _invalidar_cache()
    flash('Regla eliminada.', 'info')
    return redirect(url_for('admin.listar_precios', servicio_id=servicio_id))


@admin_bp.route('/precios/duplicar', methods=['POST'])
@login_required
@role_required('admin')
def duplicar_precios():
    origen_id = request.form.get('servicio_origen_id', type=int)
    destino_id = request.form.get('servicio_destino_id', type=int)

    if not origen_id or not destino_id:
        flash('Debe seleccionar servicio origen y destino.', 'danger')
        return redirect(url_for('admin.listar_precios'))

    if origen_id == destino_id:
        flash('El servicio origen y destino no pueden ser iguales.', 'danger')
        return redirect(url_for('admin.listar_precios'))

    reglas_origen = PrecioServicio.query.filter_by(servicio_id=origen_id).all()
    copiadas = 0
    for r in reglas_origen:
        existente = PrecioServicio.query.filter_by(
            servicio_id=destino_id,
            tipo_vehiculo_id=r.tipo_vehiculo_id,
            segmento_id=r.segmento_id,
            nivel_suciedad_id=r.nivel_suciedad_id,
        ).first()
        if existente:
            existente.precio = r.precio
            existente.duracion_minutos = r.duracion_minutos
        else:
            db.session.add(PrecioServicio(
                servicio_id=destino_id,
                tipo_vehiculo_id=r.tipo_vehiculo_id,
                segmento_id=r.segmento_id,
                nivel_suciedad_id=r.nivel_suciedad_id,
                precio=r.precio,
                duracion_minutos=r.duracion_minutos,
            ))
        copiadas += 1

    db.session.commit()
    _invalidar_cache()
    flash(f'{copiadas} reglas copiadas al servicio destino.', 'success')
    return redirect(url_for('admin.listar_precios', servicio_id=destino_id))
