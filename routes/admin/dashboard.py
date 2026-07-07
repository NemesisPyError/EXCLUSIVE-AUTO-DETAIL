from flask import render_template
from flask_login import login_required
from datetime import date
from models.reserva import Reserva
from models.estado_reserva import EstadoReserva
from routes.admin import admin_bp


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime as dt
    hoy = date.today()

    estados = {e.nombre: e.id for e in EstadoReserva.query.all()}

    reservas_hoy = Reserva.query.filter(
        Reserva.fecha == hoy
    ).count()

    pendientes = Reserva.query.filter(
        Reserva.estado_id == estados.get('Pendiente', 0)
    ).count()

    confirmadas = Reserva.query.filter(
        Reserva.estado_id == estados.get('Confirmada', 0)
    ).count()

    en_proceso = Reserva.query.filter(
        Reserva.estado_id == estados.get('En proceso', 0)
    ).count()

    finalizadas = Reserva.query.filter(
        Reserva.estado_id == estados.get('Finalizada', 0)
    ).count()

    completadas = Reserva.query.filter(
        Reserva.estado_id.in_([
            estados.get(n, 0) for n in ('Lavado terminado', 'Esperando retiro', 'Finalizada')
        ])
    ).count()

    canceladas = Reserva.query.filter(
        Reserva.estado_id == estados.get('Cancelada', 0)
    ).count()

    ahora = dt.now().time()
    from sqlalchemy.orm import joinedload
    reservas_activas = Reserva.query.options(
        joinedload(Reserva.cliente),
        joinedload(Reserva.estado),
        joinedload(Reserva.categoria_servicio),
    ).filter(
        Reserva.estado_id == estados.get('En proceso', 0),
        Reserva.fecha == hoy,
    ).all()

    tiempo_restante_total = 0
    for r in reservas_activas:
        if r.hora_fin_calculada:
            fin_min = r.hora_fin_calculada.hour * 60 + r.hora_fin_calculada.minute
            ahora_min = ahora.hour * 60 + ahora.minute
            restante = fin_min - ahora_min
            if restante > 0:
                tiempo_restante_total += restante

    from models.horario import Horario
    dia_semana = hoy.weekday() + 1
    horario_hoy = Horario.query.filter_by(dia_semana=dia_semana, activo=True).first()
    horas_disponibles = 0
    if horario_hoy:
        inicio_min = horario_hoy.hora_inicio.hour * 60 + horario_hoy.hora_inicio.minute
        fin_min = horario_hoy.hora_fin.hour * 60 + horario_hoy.hora_fin.minute
        total_min = fin_min - inicio_min
        ocupados = tiempo_restante_total
        libres = max(total_min - ocupados, 0)
        horas_disponibles = libres // 60

    ultimas_reservas = Reserva.query.order_by(
        Reserva.created_at.desc()
    ).limit(10).all()

    estados_lista = EstadoReserva.query.order_by(EstadoReserva.orden).all()

    from models.usuario import Usuario
    empleados = Usuario.query.filter_by(activo=True).order_by(Usuario.nombre).all()
    empleados_count = len(empleados)

    return render_template(
        'admin/dashboard.html',
        reservas_hoy=reservas_hoy,
        pendientes=pendientes,
        confirmadas=confirmadas,
        en_proceso=en_proceso,
        finalizadas=finalizadas,
        completadas=completadas,
        canceladas=canceladas,
        tiempo_restante_total=tiempo_restante_total,
        horas_disponibles=horas_disponibles,
        empleados_count=empleados_count,
        empleados=empleados,
        ultimas_reservas=ultimas_reservas,
        estados=estados_lista,
    )
