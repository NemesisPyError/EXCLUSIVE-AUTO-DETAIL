"""
Servicio de WhatsApp — normalización de números y mensajes.
La integración con WhatsApp Business API queda pendiente.
"""
import re


def normalize_phone(telefono):
    """Normaliza un número de teléfono paraguayo al formato internacional.
    09XXXXXXXX -> 5959XXXXXXXX, mantiene el prefijo 595 si ya lo tiene.
    Retorna solo dígitos."""
    if not telefono:
        return ''
    digitos = re.sub(r'\D', '', telefono)
    if digitos.startswith('0'):
        digitos = '595' + digitos[1:]
    elif not digitos.startswith('595'):
        digitos = '595' + digitos
    return digitos


def build_confirm_msg(reserva):
    """Construye el texto de WhatsApp para confirmación de una reserva."""
    v = reserva.vehiculos.first()
    svcs = reserva.servicios.all()
    svc_names = ', '.join(rs.servicio.nombre for rs in svcs)
    total = int(sum(rs.servicio.precio or 0 for rs in svcs))
    total_str = f'₲ {total:,}'.replace(',', '.')

    lines = [
        f'Hola *{reserva.cliente.nombre}*!, te escribimos de *Exclusive Auto Detail*.',
        '',
        f'*Reserva N° {reserva.id}*',
        f'*Fecha:* {reserva.fecha.strftime("%A %d de %B de %Y").capitalize()}',
        f'*Hora:* {reserva.hora_inicio.strftime("%H:%M")} hs',
    ]
    if v:
        lines.append(f'*Vehículo:* {v.marca} {v.modelo}')
        extras = ' '.join(filter(None, [str(v.anio) if v.anio else None, v.color]))
        if extras:
            lines.append(f'*Detalle:* {extras}')
        if v.tipo_vehiculo:
            lines.append(f'*Tipo:* {v.tipo_vehiculo.replace("_", " ").title()}')
    if svc_names:
        lines.append(f'*Servicios:* {svc_names}')
        lines.append(f'*Total:* {total_str}')
    if reserva.observaciones:
        lines.append(f'*Notas:* {reserva.observaciones}')
    lines.extend([
        '',
        'Cualquier consulta, quedamos a tu disposicion. Gracias por confiar en nosotros!',
    ])
    return '\n'.join(lines)
