from extensions import db, login_manager

from models.usuario import Usuario
from models.cliente import Cliente
from models.vehiculo import Vehiculo
from models.servicio import Servicio, CategoriaServicioEnum
from models.estado_reserva import EstadoReserva
from models.reserva import Reserva, ReservaServicio
from models.horario import Horario
from models.testimonio import Testimonio
from models.galeria import Galeria
from models.galeria_categoria import GaleriaCategoria
from models.factor_tiempo import FactorTiempo, ReservaFactorTiempo, TipoFactor

from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.tipo_lavado import TipoLavado
from models.subtipo_lavado import SubTipoLavado
from models.tipo_detallado import TipoDetallado
from models.regla_precio import ReglaPrecio
from models.reserva_item import ReservaItem
from models.estado_cambio import EstadoCambio

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


__all__ = [
    'Usuario', 'Cliente', 'Vehiculo',
    'Servicio', 'CategoriaServicioEnum',
    'CategoriaServicio',
    'EstadoReserva', 'Reserva', 'ReservaServicio',
    'ReservaItem',
    'Horario', 'Testimonio', 'Galeria', 'GaleriaCategoria',
    'FactorTiempo', 'ReservaFactorTiempo', 'TipoFactor',
    'TipoVehiculo', 'TipoLavado', 'SubTipoLavado',
    'TipoDetallado', 'ReglaPrecio', 'EstadoCambio',
]
