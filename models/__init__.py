from extensions import db, login_manager

from models.segmento import Segmento
from models.tipo_vehiculo import TipoVehiculo
from models.nivel_suciedad import NivelSuciedad
from models.marca import Marca
from models.modelo_vehiculo import ModeloVehiculo
from models.cliente import Cliente
from models.vehiculo import Vehiculo
from models.categoria_servicio import CategoriaServicio
from models.servicio import Servicio
from models.servicio_tipo_vehiculo import ServicioTipoVehiculo
from models.paquete_servicio import PaqueteServicio
from models.precio_servicio import PrecioServicio
from models.tipo_box import TipoBox
from models.box_tipo_vehiculo import BoxTipoVehiculo
from models.box import Box
from models.horario import Horario
from models.estado_reserva import EstadoReserva
from models.reserva import Reserva
from models.reserva_adicional import ReservaAdicional
from models.estado_cambio import EstadoCambio
from models.fotografia_reserva import FotografiaReserva
from models.usuario import Usuario
from models.galeria_categoria import GaleriaCategoria
from models.galeria import Galeria
from models.testimonio import Testimonio
from models.configuracion import Configuracion
from models.solicitud_catalogo import SolicitudCatalogo


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


__all__ = [
    'Segmento',
    'TipoVehiculo',
    'NivelSuciedad',
    'Marca',
    'ModeloVehiculo',
    'Cliente',
    'Vehiculo',
    'CategoriaServicio',
    'Servicio',
    'ServicioTipoVehiculo',
    'PaqueteServicio',
    'PrecioServicio',
    'TipoBox',
    'BoxTipoVehiculo',
    'Box',
    'Horario',
    'EstadoReserva',
    'Reserva',
    'ReservaAdicional',
    'EstadoCambio',
    'FotografiaReserva',
    'Usuario',
    'GaleriaCategoria',
    'Galeria',
    'Testimonio',
    'Configuracion',
    'SolicitudCatalogo',
]
