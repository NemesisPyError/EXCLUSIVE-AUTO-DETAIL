from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db, limiter
from decorators import role_required
from models.reserva import Reserva
from models.estado_reserva import EstadoReserva
from models.estado_cambio import EstadoCambio
from models.cliente import Cliente
from models.vehiculo import Vehiculo
from models.servicio import Servicio
from models.box import Box
from models.reserva_adicional import ReservaAdicional
from services.security_service import log_admin_action, log_error
from services.estado_machine import EstadoMachine
from services.whatsapp_service import normalize_phone, build_confirm_msg
from datetime import datetime
from urllib.parse import quote
import traceback
from routes.admin import admin_bp


@admin_bp.route('/reservas')
@login_required
def listar_reservas():
    from sqlalchemy.orm import joinedload
    filtro_estado = request.args.get('estado', '').strip()
    filtro_fecha = request.args.get('fecha', '').strip()
    filtro_buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Reserva.query.options(
        joinedload(Reserva.cliente),
        joinedload(Reserva.estado),
        joinedload(Reserva.usuario_asignado),
        joinedload(Reserva.servicio),
    )

    if filtro_estado:
        try:
            query = query.filter(Reserva.estado_reserva_id == int(filtro_estado))
        except (ValueError, TypeError):
            pass

    if filtro_fecha:
        try:
            f = datetime.strptime(filtro_fecha, '%Y-%m-%d').date()
            query = query.filter(Reserva.fecha == f)
        except ValueError:
            pass

    if filtro_buscar:
        like = f'%{filtro_buscar}%'
        query = query.join(Cliente).filter(
            db.or_(
                Cliente.nombre.ilike(like),
                Cliente.apellido.ilike(like),
                Cliente.telefono.ilike(like),
                Cliente.cedula.ilike(like),
            )
        )

    query = query.order_by(Reserva.fecha.desc(), Reserva.hora_inicio.desc())

    paginacion = query.paginate(
        page=page, per_page=20, error_out=False
    )

    estados = EstadoReserva.query.order_by(EstadoReserva.orden).all()

    return render_template(
        'admin/reservas.html',
        reservas=paginacion.items,
        paginacion=paginacion,
        estados=estados,
        filtro_estado=filtro_estado,
        filtro_fecha=filtro_fecha,
        filtro_buscar=filtro_buscar,
    )


@admin_bp.route('/reservas/<int:reserva_id>')
@login_required
def detalle_reserva(reserva_id):
    from sqlalchemy.orm import joinedload
    from models.usuario import Usuario
    reserva = (
        Reserva.query
        .options(
            joinedload(Reserva.cliente),
            joinedload(Reserva.estado),
            joinedload(Reserva.servicio).joinedload(Servicio.categoria),
            joinedload(Reserva.nivel_suciedad),
            joinedload(Reserva.box).joinedload(Box.tipo_box),
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.tipo_vehiculo),
            joinedload(Reserva.vehiculo).joinedload(Vehiculo.segmento),
            joinedload(Reserva.adicionales).joinedload(ReservaAdicional.servicio),
        )
        .get_or_404(reserva_id)
    )
    estados = EstadoReserva.query.order_by(EstadoReserva.orden).all()
    empleados = Usuario.query.filter_by(activo=True).order_by(Usuario.nombre).all()

    msg = build_confirm_msg(reserva)
    wa_number = normalize_phone(reserva.cliente.telefono)
    whatsapp_link = f'https://wa.me/{wa_number}?text={quote(msg)}' if wa_number else ''

    return render_template(
        'admin/reserva_detalle.html',
        reserva=reserva,
        estados=estados,
        empleados=empleados,
        whatsapp_link=whatsapp_link,
    )


@admin_bp.route('/reservas/<int:reserva_id>/estado', methods=['POST'])
@login_required
@role_required('admin')
def cambiar_estado(reserva_id):
    data = request.get_json(silent=True) or {}
    estado_id = data.get('estado_id')

    if not estado_id:
        return jsonify({'success': False, 'error': 'estado_id requerido.'}), 400

    try:
        estado_id = int(estado_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'estado_id invalido.'}), 400

    estado = db.session.get(EstadoReserva, estado_id)
    if not estado:
        return jsonify({'success': False, 'error': 'Estado no existe.'}), 404

    reserva = Reserva.query.get_or_404(reserva_id)

    if estado_id == reserva.estado_reserva_id:
        return jsonify({'success': True, 'estado_nombre': estado.nombre, 'mensaje': 'Sin cambios.'})

    ok, msg = EstadoMachine.validar_transicion(reserva.estado_reserva_id, estado_id)
    if not ok:
        return jsonify({'success': False, 'error': msg}), 400

    estado_anterior_id = reserva.estado_reserva_id
    reserva.estado_reserva_id = estado.id

    cambio = EstadoCambio(
        reserva_id=reserva.id,
        estado_anterior_id=estado_anterior_id,
        estado_nuevo_id=estado.id,
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        ip=request.remote_addr,
    )
    db.session.add(cambio)
    db.session.commit()

    log_admin_action(current_user.email, 'cambiar_estado', f'Reserva #{reserva_id} -> {estado.nombre}')
    return jsonify({'success': True, 'estado_nombre': estado.nombre})


@admin_bp.route('/reservas/<int:reserva_id>/asignar', methods=['POST'])
@login_required
@role_required('admin')
def asignar_empleado(reserva_id):
    data = request.get_json(silent=True) or {}
    empleado_id = data.get('empleado_id')

    from models.usuario import Usuario

    reserva = Reserva.query.get_or_404(reserva_id)

    if not empleado_id:
        reserva.usuario_asignado_id = None
        db.session.commit()
        return jsonify({'success': True, 'empleado_nombre': 'Sin asignar', 'mensaje': 'Asignacion removida.'})

    empleado = Usuario.query.get(empleado_id)
    if not empleado or not empleado.activo:
        return jsonify({'success': False, 'error': 'Empleado no encontrado o inactivo.'}), 404

    reserva.usuario_asignado_id = empleado.id
    db.session.commit()
    log_admin_action(current_user.email, 'asignar_empleado', f'Reserva #{reserva_id} -> {empleado.nombre}')
    return jsonify({'success': True, 'empleado_nombre': empleado.nombre, 'mensaje': 'Empleado asignado.'})


@admin_bp.route('/reservas/<int:reserva_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_reserva(reserva_id):
    from sqlalchemy.orm import joinedload
    reserva = (
        Reserva.query
        .options(
            joinedload(Reserva.cliente),
            joinedload(Reserva.vehiculo),
            joinedload(Reserva.servicio),
            joinedload(Reserva.estado),
            joinedload(Reserva.box),
        )
        .get_or_404(reserva_id)
    )

    if request.method == 'GET':
        return render_template('admin/editar_reserva.html', reserva=reserva)

    data = request.form
    try:
        cliente = reserva.cliente
        cliente.nombre = data.get('nombre', cliente.nombre)
        cliente.apellido = data.get('apellido', cliente.apellido)
        cliente.cedula = data.get('cedula') or cliente.cedula
        cliente.telefono = data.get('telefono', cliente.telefono)
        cliente.email = data.get('email') or cliente.email

        vehiculo = reserva.vehiculo
        if vehiculo:
            vehiculo.marca_texto = data.get('marca', vehiculo.marca_texto)
            vehiculo.modelo_texto = data.get('modelo', vehiculo.modelo_texto)
            vehiculo.anio = int(data.get('anio')) if data.get('anio') else vehiculo.anio
            vehiculo.color = data.get('color', vehiculo.color)

        reserva.observaciones_internas = data.get('observaciones', reserva.observaciones_internas)

        db.session.commit()
        flash('Reserva actualizada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error(
            '/admin/reservas/editar',
            f'Reserva #{reserva_id}: {type(e).__name__}: {e}\n{traceback.format_exc()}'
        )
        flash('Error al actualizar la reserva.', 'danger')

    return redirect(url_for('admin.detalle_reserva', reserva_id=reserva.id))


@admin_bp.route('/reservas/<int:reserva_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
@limiter.limit("15 per minute")
def eliminar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    try:
        db.session.delete(reserva)
        db.session.commit()
        log_admin_action(current_user.email, 'eliminar_reserva', f'Reserva #{reserva_id}')
        flash('Reserva eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error('/admin/reservas/eliminar', str(e))
        flash('Error al eliminar la reserva.', 'danger')

    return redirect(url_for('admin.listar_reservas'))


@admin_bp.route('/reservas/eliminar-masivo', methods=['POST'])
@login_required
@role_required('admin')
@limiter.limit("5 per minute")
def eliminar_reservas_masivo():
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])

    if not ids or not isinstance(ids, list):
        return jsonify({'success': False, 'error': 'Lista de IDs requerida.'}), 400

    try:
        reservas = Reserva.query.filter(Reserva.id.in_(ids)).all()
        for r in reservas:
            db.session.delete(r)
        db.session.commit()
        log_admin_action(current_user.email, 'eliminar_reservas_masivo', f'{len(reservas)} reservas')
        return jsonify({'success': True, 'eliminados': len(reservas)})
    except Exception as e:
        db.session.rollback()
        log_error('/admin/reservas/eliminar-masivo', str(e))
        return jsonify({'success': False, 'error': 'Error al procesar la solicitud.'}), 500
