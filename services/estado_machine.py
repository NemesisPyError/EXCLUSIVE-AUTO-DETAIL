from extensions import db
from models.estado_reserva import EstadoReserva


class EstadoMachine:

    TRANSICIONES = {
        'Pendiente':   ['Confirmada', 'Cancelada'],
        'Confirmada':  ['Recibida', 'Cancelada'],
        'Recibida':    ['En Proceso', 'Cancelada'],
        'En Proceso':  ['Lista', 'Cancelada'],
        'Lista':       ['Entregada'],
        'Entregada':   [],
        'Cancelada':   [],
    }

    @classmethod
    def validar_transicion(cls, estado_actual_id, estado_nuevo_id):
        if estado_actual_id == estado_nuevo_id:
            return True, ''

        actual = db.session.get(EstadoReserva, estado_actual_id)
        nuevo = db.session.get(EstadoReserva, estado_nuevo_id)

        if not actual or not nuevo:
            return False, 'Estado no encontrado.'

        permitidos = cls.TRANSICIONES.get(actual.nombre, [])

        if nuevo.nombre in permitidos:
            return True, ''

        return False, (
            f'No se puede cambiar de "{actual.nombre}" a "{nuevo.nombre}". '
            f'Transiciones permitidas desde "{actual.nombre}": '
            f'{", ".join(permitidos) if permitidos else "ninguna (estado terminal)"}.'
        )
