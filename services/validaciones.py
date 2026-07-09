import re
from datetime import date, timedelta
from services.duracion import PlanificadorOcupacion


def validar_email(email):
    if not email:
        return True, ''
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ''
    return False, 'El formato del email no es valido.'


def validar_telefono_py(telefono):
    if not telefono:
        return False, 'El telefono es obligatorio.'
    limpio = re.sub(r'[\s\-\(\)\+]', '', telefono)
    if re.match(r'^5959\d{8}$', limpio) or re.match(r'^09\d{8}$', limpio):
        return True, ''
    return False, 'Ingresa un numero de telefono paraguayo valido (0991XXXXXX o +595991XXXXXX).'


def validar_fecha_futura(fecha):
    if fecha < date.today():
        return False, 'La fecha debe ser hoy o un dia futuro.'
    return True, ''


def validar_dentro_horario(dia_semana, hora, duracion_min):
    horario = PlanificadorOcupacion.horario_activo(dia_semana)
    if not horario:
        return False, 'El taller no atiende ese dia.'
    if hora < horario.hora_inicio:
        return False, f'El horario comienza a las {horario.hora_inicio.strftime("%H:%M")}.'
    from datetime import datetime, timedelta
    hora_fin = (datetime.combine(date.today(), hora) + timedelta(minutes=duracion_min)).time()
    if hora_fin > horario.hora_fin:
        return False, f'El servicio debe terminar antes de las {horario.hora_fin.strftime("%H:%M")}.'
    return True, ''


def validar_disponibilidad(tipo_vehiculo_id, fecha, hora, duracion_min):
    box = PlanificadorOcupacion.asignar_box(tipo_vehiculo_id, fecha, hora, duracion_min)
    if box is None:
        return False, 'No hay box disponible en ese horario. Intenta con otro dia u horario.'
    return True, box.id
