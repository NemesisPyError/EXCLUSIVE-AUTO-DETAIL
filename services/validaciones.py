import re
from datetime import date, datetime, timedelta


def validar_email(email):
    if not email or not isinstance(email, str):
        return False
    patron = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email.strip()))


def validar_telefono_paraguay(tel):
    if not tel or not isinstance(tel, str):
        return False
    tel = tel.strip()
    patrones = [
        r'^\+595\d{9}$',
        r'^09\d{8}$',
        r'^\(09\d{2}\)\s?\d{3}\-?\d{3}$',
    ]
    return any(re.match(p, tel) for p in patrones)


def validar_fecha_futura(fecha):
    if not fecha:
        return False
    return fecha >= date.today()


def validar_capacidad_horario(fecha, hora):
    from models.horario import Horario
    from models.reserva import Reserva

    dia = fecha.weekday() + 1
    horario = Horario.query.filter_by(
        dia_semana=dia, activo=True
    ).first()

    if not horario:
        return False, 0, 'El taller no opera este dia.'

    reservas_count = Reserva.query.filter(
        Reserva.fecha == fecha,
        Reserva.hora_inicio == hora
    ).count()

    lugares_restantes = horario.capacidad_maxima - reservas_count
    disponible = reservas_count < horario.capacidad_maxima
    return disponible, lugares_restantes, None


def validar_disponibilidad_por_rango(fecha, hora_inicio, duracion_min, lock_rows=False):
    from services.duracion import PlanificadorOcupacion
    return PlanificadorOcupacion.validar_reserva(fecha, hora_inicio, duracion_min, lock_rows=lock_rows)


def validar_precio_estimado(precio_estimado, precio_fijo):
    if precio_estimado is not None and precio_estimado < 0:
        return False, 'El precio estimado no puede ser negativo.'
    if precio_fijo is not None and precio_fijo < 0:
        return False, 'El precio fijo no puede ser negativo.'
    return True, None


def validar_tiempo_estimado(tiempo_min):
    if tiempo_min is None or tiempo_min < 0:
        return False, 'El tiempo estimado debe ser mayor o igual a 0.'
    return True, None


def validar_dias_bloqueo(dias):
    if dias is None or dias < 0:
        return False, 'Los dias de bloqueo deben ser mayor o igual a 0.'
    return True, None


def validar_combinacion_precio(regla_precio):
    tiene_precio_fijo = regla_precio.precio_fijo is not None
    tiene_precio_estimado = regla_precio.precio_estimado is not None

    if not tiene_precio_fijo and not tiene_precio_estimado:
        return False, 'Debe especificar al menos un precio (fijo o estimado).'

    if regla_precio.es_precio_estimado and not tiene_precio_estimado:
        return False, 'Si es precio estimado, debe proporcionar precio_estimado.'

    return True, None
