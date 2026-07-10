from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.servicio import Servicio
from models.marca import Marca
from models.modelo_vehiculo import ModeloVehiculo


def serialize_tipo_vehiculo(tv: TipoVehiculo) -> dict:
    return {
        'id': tv.id,
        'nombre': tv.nombre,
        'slug': tv.slug,
        'icono': tv.icono,
        'orden': tv.orden,
        'descripcion': tv.descripcion,
    }


def serialize_categoria(cat: CategoriaServicio) -> dict:
    return {
        'id': cat.id,
        'nombre': cat.nombre,
        'slug': cat.slug,
        'orden': cat.orden,
    }


def serialize_servicio(svc: Servicio, composicion=None) -> dict:
    result = {
        'id': svc.id,
        'nombre': svc.nombre,
        'slug': svc.slug,
        'descripcion': svc.descripcion,
        'tipo': svc.tipo,
        'categoria_id': svc.categoria_servicio_id,
        'categoria_nombre': svc.categoria.nombre if svc.categoria else '',
        'requiere_inspeccion_previa': svc.requiere_inspeccion_previa,
        'requiere_varios_dias': svc.requiere_varios_dias,
        'dias_bloqueo': svc.dias_bloqueo,
        'activo': svc.activo,
    }
    if svc.tipo == 'paquete' and composicion is not None:
        result['composicion'] = [
            {
                'servicio_id': c.servicio_id,
                'nombre': c.servicio.nombre if c.servicio else '',
                'es_principal': c.es_principal,
                'orden': c.orden,
            }
            for c in composicion
        ]
    return result


def serialize_precio(precio) -> dict:
    return {
        'id': precio.id,
        'servicio_id': precio.servicio_id,
        'tipo_vehiculo_id': precio.tipo_vehiculo_id,
        'segmento_id': precio.segmento_id,
        'nivel_suciedad_id': precio.nivel_suciedad_id,
        'precio': precio.precio,
        'duracion_minutos': precio.duracion_minutos,
    }


def serialize_marca(marca: Marca) -> dict:
    return {
        'id': marca.id,
        'nombre': marca.nombre,
        'slug': marca.slug,
        'pais_origen': marca.pais_origen,
        'logo': marca.logo,
    }


def serialize_modelo(mv: ModeloVehiculo) -> dict:
    return {
        'id': mv.id,
        'marca_id': mv.marca_id,
        'marca_nombre': mv.marca.nombre if mv.marca else '',
        'nombre': mv.nombre,
        'slug': mv.slug,
        'tipo_vehiculo_id': mv.tipo_vehiculo_id,
        'tipo_vehiculo_nombre': mv.tipo_vehiculo.nombre if mv.tipo_vehiculo else '',
        'segmento_id': mv.segmento_id,
        'segmento_nombre': mv.segmento.nombre if mv.segmento else '',
        'anio_desde': mv.anio_desde,
        'anio_hasta': mv.anio_hasta,
    }
