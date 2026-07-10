"""
Servicio de WhatsApp — normalizacion de numeros y mensajes.
La integracion con WhatsApp Business API queda pendiente.
"""
import re


def normalize_phone(telefono):
    digitos = re.sub(r'\D', '', telefono or '')
    if not digitos:
        return ''
    if digitos.startswith('0'):
        digitos = '595' + digitos[1:]
    elif not digitos.startswith('595'):
        digitos = '595' + digitos
    return digitos


def build_confirm_msg(reserva):
    v = reserva.vehiculo
    svc = reserva.servicio
    adicionales = reserva.adicionales
    total = reserva.precio_estimado_base + reserva.precio_estimado_adicionales
    total_str = f'Gs {total:,}'.replace(',', '.')

    lines = [
        f'Hola *{reserva.cliente.nombre}*!, te escribimos de *Exclusive Auto Detail*.',
        '',
        f'*Reserva N {reserva.id}*',
        f'*Fecha:* {_fmt_fecha(reserva.fecha)}',
        f'*Hora:* {reserva.hora_inicio.strftime("%H:%M")} hs',
    ]

    if v:
        marca = v.marca.nombre if v.marca else v.marca_texto or ''
        modelo = v.modelo.nombre if v.modelo else v.modelo_texto or ''
        lines.append(f'*Vehiculo:* {marca} {modelo}'.strip())
        extras = ' '.join(filter(None, [str(v.anio) if v.anio else None, v.color]))
        if extras:
            lines.append(f'*Detalle:* {extras}')
        if v.tipo_vehiculo:
            lines.append(f'*Tipo:* {v.tipo_vehiculo.nombre}')

    if svc:
        lines.append(f'*Servicio:* {svc.nombre}')
        lines.append(f'*Total:* {total_str}')

    if adicionales:
        ad_names = ', '.join(a.servicio.nombre for a in adicionales)
        lines.append(f'*Adicionales:* {ad_names}')

    if reserva.observaciones_cliente:
        lines.append(f'*Notas:* {reserva.observaciones_cliente}')

    lines.extend([
        '',
        'Cualquier consulta, quedamos a tu disposicion. Gracias por confiar en nosotros!',
    ])
    return '\n'.join(lines)


def _fmt_fecha(fecha):
    meses = [
        '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
    ]
    return fecha.strftime(f'%d de {meses[fecha.month]} de %Y')
