import hashlib
from extensions import db, cache
from models.regla_precio import ReglaPrecio
from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.tipo_lavado import TipoLavado
from models.subtipo_lavado import SubTipoLavado
from models.tipo_detallado import TipoDetallado

# Claves de cache con prefijo global 'exclusive_autodetail:'
# agregado automaticamente por CACHE_KEY_PREFIX en config.py.
# Almacenamiento real: exclusive_autodetail:pricing:version
_PRICING_VER_KEY = 'pricing:version'
_PRICING_KEY_TPL = 'precio:v{ver}:{hash}'
_PRICING_REGLA_TPL = 'precio:regla:{rid}'


class PricingEngine:

    @staticmethod
    def _precio_cache_key(**kwargs):
        clean = {k: v for k, v in sorted(kwargs.items()) if v is not None}
        raw = str(sorted(clean.items()))
        h = hashlib.md5(raw.encode()).hexdigest()
        ver = cache.get(_PRICING_VER_KEY) or 0
        return _PRICING_KEY_TPL.format(ver=ver, hash=h)

    @staticmethod
    def invalidar_cache_precio():
        cache.set(_PRICING_VER_KEY, (cache.get(_PRICING_VER_KEY) or 0) + 1)

    @staticmethod
    def obtener_precio(**kwargs):
        cache_key = PricingEngine._precio_cache_key(**kwargs)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, None

        vehiculo_slug       = kwargs.get('vehiculo_slug')
        categoria_slug      = kwargs.get('categoria_slug')
        tipo_lavado_slug    = kwargs.get('tipo_lavado_slug')
        subtipo_slug        = kwargs.get('subtipo_slug')
        tipo_detallado_slug = kwargs.get('tipo_detallado_slug')
        servicio_id         = kwargs.get('servicio_id')

        vehiculo = TipoVehiculo.query.filter_by(slug=vehiculo_slug, activo=True).first()
        if not vehiculo:
            return None, 'Tipo de vehiculo no encontrado o inactivo.'

        categoria = CategoriaServicio.query.filter_by(slug=categoria_slug, activo=True).first()
        if not categoria:
            return None, 'Categoria de servicio no encontrada o inactiva.'

        query = ReglaPrecio.query.filter_by(
            categoria_servicio_id=categoria.id,
            tipo_vehiculo_id=vehiculo.id,
            activo=True,
        )

        if tipo_lavado_slug:
            tl = TipoLavado.query.filter_by(slug=tipo_lavado_slug, activo=True).first()
            if not tl:
                return None, 'Tipo de lavado no encontrado.'
            query = query.filter(ReglaPrecio.tipo_lavado_id == tl.id)

        if subtipo_slug:
            st = SubTipoLavado.query.filter_by(slug=subtipo_slug, activo=True).first()
            if not st:
                return None, 'Subtipo de lavado no encontrado.'
            query = query.filter(ReglaPrecio.subtipo_lavado_id == st.id)

        if tipo_detallado_slug:
            td = TipoDetallado.query.filter_by(slug=tipo_detallado_slug, activo=True).first()
            if not td:
                return None, 'Tipo de detallado no encontrado.'
            query = query.filter(ReglaPrecio.tipo_detallado_id == td.id)

        if servicio_id:
            query = query.filter(ReglaPrecio.servicio_id == servicio_id)

        regla = query.first()

        if not regla:
            return None, 'No se encontro una regla de precio para esta combinacion.'

        resultado = {
            'regla_id':               regla.id,
            'precio_fijo':            float(regla.precio_fijo) if regla.precio_fijo is not None else None,
            'precio_estimado':        float(regla.precio_estimado) if regla.precio_estimado is not None else None,
            'es_precio_estimado':     regla.es_precio_estimado,
            'tiempo_estimado_min':    regla.tiempo_estimado_min,
            'dias_bloqueo':           regla.dias_bloqueo,
            'descripcion_publica':    regla.descripcion_publica,
            'nota_inspeccion':        regla.nota_inspeccion,
        }
        cache.set(cache_key, resultado, timeout=3600)
        return resultado, None

    @staticmethod
    def obtener_precio_por_regla(regla_id):
        cache_key = _PRICING_REGLA_TPL.format(rid=regla_id)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, None

        regla = ReglaPrecio.query.get(regla_id)
        if not regla or not regla.activo:
            return None, 'Regla de precio no encontrada.'

        resultado = {
            'regla_id':               regla.id,
            'precio_fijo':            float(regla.precio_fijo) if regla.precio_fijo is not None else None,
            'precio_estimado':        float(regla.precio_estimado) if regla.precio_estimado is not None else None,
            'es_precio_estimado':     regla.es_precio_estimado,
            'tiempo_estimado_min':    regla.tiempo_estimado_min,
            'dias_bloqueo':           regla.dias_bloqueo,
            'descripcion_publica':    regla.descripcion_publica,
            'nota_inspeccion':        regla.nota_inspeccion,
        }
        cache.set(cache_key, resultado, timeout=3600)
        return resultado, None
