from flask import Blueprint, jsonify, request
from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.servicio import Servicio
from models.marca import Marca
from models.modelo_vehiculo import ModeloVehiculo
from models.segmento import Segmento
from models.nivel_suciedad import NivelSuciedad
from services.pricing_service import PricingEngine
from services.validaciones import validar_fecha_futura
from services.duracion import PlanificadorOcupacion
from services.serializers import (
    serialize_tipo_vehiculo,
    serialize_categoria,
    serialize_marca,
    serialize_modelo,
    serialize_servicio,
    serialize_precio,
)
from extensions import limiter, cache, _view_cache_key
from sqlalchemy.orm import joinedload

api_publica_bp = Blueprint('api_publica', __name__)


@api_publica_bp.route('/tipos-vehiculo')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/tipos-vehiculo'))
def tipos_vehiculo():
    items = TipoVehiculo.query.order_by(
        TipoVehiculo.orden, TipoVehiculo.id
    ).all()
    return jsonify({
        'success': True,
        'tipos_vehiculo': [serialize_tipo_vehiculo(t) for t in items],
    })


@api_publica_bp.route('/categorias-servicio')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/categorias-servicio'))
def categorias_servicio():
    items = CategoriaServicio.query.order_by(
        CategoriaServicio.orden, CategoriaServicio.id
    ).all()
    return jsonify({
        'success': True,
        'categorias': [serialize_categoria(c) for c in items],
    })


@api_publica_bp.route('/segmentos')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/segmentos'))
def segmentos():
    items = Segmento.query.order_by(Segmento.orden, Segmento.id).all()
    return jsonify({
        'success': True,
        'segmentos': [{'id': s.id, 'nombre': s.nombre, 'slug': s.slug} for s in items],
    })


@api_publica_bp.route('/niveles-suciedad')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/niveles-suciedad'))
def niveles_suciedad():
    items = NivelSuciedad.query.order_by(NivelSuciedad.orden, NivelSuciedad.id).all()
    return jsonify({
        'success': True,
        'niveles': [{'id': n.id, 'nombre': n.nombre, 'descripcion': n.descripcion} for n in items],
    })


@api_publica_bp.route('/servicios')
@cache.cached(timeout=3600, key_prefix=lambda: _view_cache_key('/api/publica/servicios', include_qs=True))
def servicios():
    tipo = request.args.get('tipo', '').strip()
    categoria_slug = request.args.get('categoria_slug', '').strip()

    query = Servicio.query.options(
        joinedload(Servicio.categoria)
    ).filter_by(activo=True, deleted_at=None)

    if tipo:
        query = query.filter(Servicio.tipo == tipo)
    if categoria_slug:
        query = query.join(CategoriaServicio).filter(CategoriaServicio.slug == categoria_slug)

    items = query.order_by(Servicio.tipo, Servicio.nombre).all()

    composiciones = {}
    paquetes_ids = [s.id for s in items if s.tipo == 'paquete']
    if paquetes_ids:
        from models.paquete_servicio import PaqueteServicio
        comps = (
            PaqueteServicio.query
            .options(joinedload(PaqueteServicio.servicio))
            .filter(PaqueteServicio.paquete_id.in_(paquetes_ids))
            .order_by(PaqueteServicio.paquete_id, PaqueteServicio.orden)
            .all()
        )
        for c in comps:
            composiciones.setdefault(c.paquete_id, []).append(c)

    return jsonify({
        'success': True,
        'servicios': [serialize_servicio(s, composiciones.get(s.id)) for s in items],
    })


@api_publica_bp.route('/precio')
@limiter.limit("30 per minute")
def consultar_precio():
    servicio_id = request.args.get('servicio_id', type=int)
    tipo_vehiculo_id = request.args.get('tipo_vehiculo_id', type=int)
    segmento_id = request.args.get('segmento_id', type=int)
    nivel_suciedad_id = request.args.get('nivel_suciedad_id', type=int)

    if not all([servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id]):
        return jsonify({
            'success': False,
            'error': 'Parametros requeridos: servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id.',
        }), 400

    resultado = PricingEngine.obtener_precio(
        servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id
    )

    if not resultado:
        return jsonify({'success': False, 'error': 'No hay precio configurado.'}), 404

    return jsonify({
        'success': True,
        'precio': resultado,
    })


@api_publica_bp.route('/disponibilidad')
def disponibilidad():
    tipo_vehiculo_id = request.args.get('tipo_vehiculo_id', type=int)
    fecha_str = request.args.get('fecha', '').strip()
    duracion_str = request.args.get('duracion_min', '60')

    from datetime import datetime as dt

    if not fecha_str or not tipo_vehiculo_id:
        return jsonify({'success': False, 'error': 'Parametros requeridos.'}), 400

    try:
        fecha = dt.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Formato de fecha invalido.'}), 400

    if not validar_fecha_futura(fecha):
        return jsonify({'success': False, 'error': 'La fecha debe ser hoy o futura.'}), 400

    duracion_min = int(duracion_str) if duracion_str else 60
    slots = PlanificadorOcupacion.slots_disponibles(fecha, duracion_min, tipo_vehiculo_id)

    return jsonify({
        'success': True,
        'fecha': fecha_str,
        'duracion_min': duracion_min,
        'slots': slots,
    })


@api_publica_bp.route('/marcas/buscar')
@cache.cached(timeout=3600, key_prefix=lambda: _view_cache_key('/api/publica/marcas/buscar', include_qs=True))
def buscar_marcas():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'success': True, 'marcas': []})

    items = Marca.query.filter(
        Marca.activo == True,
        Marca.nombre.ilike(f'%{q}%')
    ).order_by(Marca.nombre).limit(12).all()

    return jsonify({
        'success': True,
        'marcas': [serialize_marca(m) for m in items],
    })


@api_publica_bp.route('/modelos/buscar')
@cache.cached(timeout=3600, key_prefix=lambda: _view_cache_key('/api/publica/modelos/buscar', include_qs=True))
def buscar_modelos():
    from sqlalchemy.orm import joinedload
    q = request.args.get('q', '').strip()
    marca_id = request.args.get('marca_id', type=int)
    marca_slug = request.args.get('marca_slug', '').strip()

    if not q and not marca_id and not marca_slug:
        return jsonify({'success': True, 'modelos': []})

    query = ModeloVehiculo.query.options(
        joinedload(ModeloVehiculo.marca),
        joinedload(ModeloVehiculo.tipo_vehiculo),
        joinedload(ModeloVehiculo.segmento),
    ).filter(ModeloVehiculo.activo == True)

    if marca_id:
        query = query.filter(ModeloVehiculo.marca_id == marca_id)
    elif marca_slug:
        marca = Marca.query.filter_by(slug=marca_slug, activo=True).first()
        if marca:
            query = query.filter(ModeloVehiculo.marca_id == marca.id)
        else:
            return jsonify({'success': True, 'modelos': []})

    if q:
        query = query.filter(ModeloVehiculo.nombre.ilike(f'%{q}%'))

    items = query.order_by(ModeloVehiculo.nombre).limit(20).all()

    return jsonify({
        'success': True,
        'modelos': [serialize_modelo(mv) for mv in items],
    })


@api_publica_bp.route('/modelos/detectar-marca')
@cache.cached(timeout=3600, key_prefix=lambda: _view_cache_key('/api/publica/modelos/detectar-marca', include_qs=True))
def detectar_marca_desde_modelo():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'success': True, 'marca': None})

    modelo = ModeloVehiculo.query.filter(
        ModeloVehiculo.activo == True,
        ModeloVehiculo.nombre.ilike(f'%{q}%')
    ).first()

    if modelo and modelo.marca:
        return jsonify({
            'success': True,
            'marca': serialize_marca(modelo.marca),
        })

    return jsonify({'success': True, 'marca': None})
