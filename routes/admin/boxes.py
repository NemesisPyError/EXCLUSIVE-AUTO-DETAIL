from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.box import Box
from models.tipo_box import TipoBox
from models.box_tipo_vehiculo import BoxTipoVehiculo
from models.tipo_vehiculo import TipoVehiculo
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache


# =============================================================
# TIPOS DE BOX
# =============================================================
@admin_bp.route('/tipos-box')
@login_required
@role_required('admin')
def listar_tipos_box():
    from sqlalchemy.orm import joinedload
    items = TipoBox.query.order_by(TipoBox.nombre).all()
    tipos_vehiculo = TipoVehiculo.query.order_by(TipoVehiculo.orden).all()
    compatibilidades = {}
    for tb in items:
        compat = db.session.query(BoxTipoVehiculo.tipo_vehiculo_id).filter_by(tipo_box_id=tb.id).all()
        compatibilidades[tb.id] = [c[0] for c in compat]
    return render_template(
        'admin/tipos_box.html',
        items=items,
        tipos_vehiculo=tipos_vehiculo,
        compatibilidades=compatibilidades,
    )


@admin_bp.route('/tipos-box/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_tipo_box():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_tipos_box'))
    if TipoBox.query.filter_by(nombre=nombre).first():
        flash('Ya existe un tipo con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_tipos_box'))
    tb = TipoBox(
        nombre=nombre,
        descripcion=(request.form.get('descripcion') or '').strip() or None,
    )
    db.session.add(tb)
    db.session.flush()
    _guardar_compatibilidades(tb.id)
    db.session.commit()
    _invalidar_cache()
    flash(f'Tipo de box "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_tipos_box'))


@admin_bp.route('/tipos-box/<int:tb_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_tipo_box(tb_id):
    tb = TipoBox.query.get_or_404(tb_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_tipos_box'))
    existente = TipoBox.query.filter(TipoBox.nombre == nombre, TipoBox.id != tb_id).first()
    if existente:
        flash('Ya existe otro tipo con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_tipos_box'))
    tb.nombre = nombre
    tb.descripcion = (request.form.get('descripcion') or '').strip() or None
    db.session.flush()
    db.session.query(BoxTipoVehiculo).filter_by(tipo_box_id=tb.id).delete()
    _guardar_compatibilidades(tb.id)
    db.session.commit()
    _invalidar_cache()
    flash(f'Tipo de box "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_tipos_box'))


def _guardar_compatibilidades(tipo_box_id):
    compatibles = request.form.getlist('tipos_vehiculo')
    for tv_id in compatibles:
        db.session.add(BoxTipoVehiculo(
            tipo_box_id=tipo_box_id,
            tipo_vehiculo_id=int(tv_id),
        ))


# =============================================================
# BOXES
# =============================================================
@admin_bp.route('/boxes')
@login_required
@role_required('admin')
def listar_boxes():
    from sqlalchemy.orm import joinedload
    items = Box.query.options(
        joinedload(Box.tipo_box)
    ).order_by(Box.tipo_box_id, Box.orden).all()
    tipos_box = TipoBox.query.order_by(TipoBox.nombre).all()
    return render_template(
        'admin/boxes.html',
        items=items,
        tipos_box=tipos_box,
    )


@admin_bp.route('/boxes/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_box():
    nombre = (request.form.get('nombre') or '').strip()
    tipo_box_id = request.form.get('tipo_box_id', type=int)
    if not nombre:
        flash('El nombre del box es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_boxes'))
    if not tipo_box_id:
        flash('El tipo de box es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_boxes'))
    if Box.query.filter_by(nombre=nombre).first():
        flash('Ya existe un box con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_boxes'))
    box = Box(
        tipo_box_id=tipo_box_id,
        nombre=nombre,
        orden=int(request.form.get('orden', 0)),
        activo=True,
    )
    db.session.add(box)
    db.session.commit()
    _invalidar_cache()
    flash(f'Box "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_boxes'))


@admin_bp.route('/boxes/<int:box_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_box(box_id):
    box = Box.query.get_or_404(box_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_boxes'))
    existente = Box.query.filter(Box.nombre == nombre, Box.id != box_id).first()
    if existente:
        flash('Ya existe otro box con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_boxes'))
    box.nombre = nombre
    box.tipo_box_id = request.form.get('tipo_box_id', type=int) or box.tipo_box_id
    box.orden = int(request.form.get('orden', box.orden))
    box.activo = request.form.get('activo', '1') == '1'
    db.session.commit()
    _invalidar_cache()
    flash(f'Box "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_boxes'))


@admin_bp.route('/boxes/<int:box_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_box(box_id):
    box = Box.query.get_or_404(box_id)
    box.activo = not box.activo
    db.session.commit()
    _invalidar_cache()
    estado = 'activado' if box.activo else 'desactivado'
    return jsonify({'success': True, 'activo': box.activo, 'mensaje': f'Box {estado}.'})


@admin_bp.route('/agenda')
@login_required
def agenda():
    from datetime import date as date_type, datetime as dt, timedelta
    from services.duracion import PlanificadorOcupacion

    fecha_str = request.args.get('fecha', '')
    if fecha_str:
        try:
            fecha = dt.strptime(fecha_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            fecha = date_type.today()
    else:
        fecha = date_type.today()

    ayer = fecha - timedelta(days=1)
    manana = fecha + timedelta(days=1)

    agenda_data = PlanificadorOcupacion.obtener_agenda_dia(fecha)

    return render_template(
        'admin/agenda.html',
        fecha=fecha,
        ayer=ayer,
        manana=manana,
        boxes=agenda_data['boxes'],
        horas=agenda_data['horas'],
        horas_objs=agenda_data['horas_objs'],
        reservas_por_box=agenda_data['reservas'],
    )


@admin_bp.route('/reservas/<int:reserva_id>/reasignar-box', methods=['POST'])
@login_required
@role_required('admin')
def reasignar_box(reserva_id):
    from models.reserva import Reserva
    reserva = Reserva.query.get_or_404(reserva_id)
    box_id = request.form.get('box_id', type=int)

    if not box_id:
        reserva.box_id = None
        db.session.commit()
        flash('Box desasignado de la reserva.', 'info')
        return redirect(request.referrer or url_for('admin.listar_reservas'))

    box = Box.query.get(box_id)
    if not box:
        flash('Box no encontrado.', 'danger')
        return redirect(request.referrer or url_for('admin.listar_reservas'))

    from services.duracion import PlanificadorOcupacion
    if not PlanificadorOcupacion.hay_disponibilidad(
        box.id, reserva.fecha, reserva.hora_inicio, reserva.duracion_total_min
    ):
        flash('El box seleccionado no esta disponible en ese horario.', 'danger')
        return redirect(request.referrer or url_for('admin.listar_reservas'))

    reserva.box_id = box.id
    db.session.commit()
    flash(f'Reserva reasignada a {box.nombre}.', 'success')
    return redirect(request.referrer or url_for('admin.listar_reservas'))
