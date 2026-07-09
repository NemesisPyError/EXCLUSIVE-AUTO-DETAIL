from extensions import db, cache
from models.precio_servicio import PrecioServicio
from models.servicio import Servicio


class PricingEngine:
    CACHE_PREFIX = 'pricing:'

    @staticmethod
    def _make_cache_key(servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id):
        key = f'{PricingEngine.CACHE_PREFIX}v{{version}}/{servicio_id}/{tipo_vehiculo_id}/{segmento_id}/{nivel_suciedad_id}'
        version = cache.get('pricing:epoch') or 0
        return key.replace('{version}', str(version))

    @classmethod
    def obtener_precio(cls, servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id):
        if not all([servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id]):
            return None

        cache_key = cls._make_cache_key(
            servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        precio_record = db.session.query(PrecioServicio).filter_by(
            servicio_id=servicio_id,
            tipo_vehiculo_id=tipo_vehiculo_id,
            segmento_id=segmento_id,
            nivel_suciedad_id=nivel_suciedad_id,
        ).first()

        if not precio_record:
            result = None
        else:
            result = {
                'precio': precio_record.precio,
                'duracion_minutos': precio_record.duracion_minutos,
            }

        cache.set(cache_key, result, timeout=600)
        return result

    @classmethod
    def obtener_precios_servicio(cls, servicio_id):
        cache_key = f'{PricingEngine.CACHE_PREFIX}v{{version}}/all/{servicio_id}'
        version = cache.get('pricing:epoch') or 0
        cache_key = cache_key.replace('{version}', str(version))

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        precios = db.session.query(PrecioServicio).filter_by(
            servicio_id=servicio_id
        ).all()

        result = [
            {
                'tipo_vehiculo_id': p.tipo_vehiculo_id,
                'segmento_id': p.segmento_id,
                'nivel_suciedad_id': p.nivel_suciedad_id,
                'precio': p.precio,
                'duracion_minutos': p.duracion_minutos,
            }
            for p in precios
        ]

        cache.set(cache_key, result, timeout=600)
        return result

    @classmethod
    def invalidar_cache_precio(cls):
        version = (cache.get('pricing:epoch') or 0) + 1
        cache.set('pricing:epoch', version)
