from flask import Blueprint, jsonify, request
from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.tipo_lavado import TipoLavado
from models.subtipo_lavado import SubTipoLavado
from models.tipo_detallado import TipoDetallado
from models.regla_precio import ReglaPrecio
from services.pricing_service import PricingEngine
from services.validaciones import validar_fecha_futura
from services.duracion import PlanificadorOcupacion
from services.serializers import (
    serialize_vehiculo,
    serialize_categoria,
    serialize_lavado,
    serialize_subtipo,
    serialize_detallado,
)
from extensions import limiter, cache, _view_cache_key

api_publica_bp = Blueprint('api_publica', __name__)


# ===================================================================
# Tipos de Vehiculo
# ===================================================================
@api_publica_bp.route('/tipos-vehiculo')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/tipos-vehiculo'))
def tipos_vehiculo():
    items = TipoVehiculo.query.filter_by(activo=True).order_by(
        TipoVehiculo.orden, TipoVehiculo.id
    ).all()
    return jsonify({
        'success': True,
        'tipos_vehiculo': [serialize_vehiculo(t) for t in items],
    })


# ===================================================================
# Categorias de Servicio
# ===================================================================
@api_publica_bp.route('/categorias-servicio')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/categorias-servicio'))
def categorias_servicio():
    items = CategoriaServicio.query.filter_by(activo=True).order_by(
        CategoriaServicio.orden, CategoriaServicio.id
    ).all()
    return jsonify({
        'success': True,
        'categorias': [serialize_categoria(c) for c in items],
    })


# ===================================================================
# Tipos de Lavado
# ===================================================================
@api_publica_bp.route('/tipos-lavado')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/tipos-lavado'))
def tipos_lavado():
    items = TipoLavado.query.filter_by(activo=True).order_by(
        TipoLavado.orden, TipoLavado.id
    ).all()
    return jsonify({
        'success': True,
        'tipos_lavado': [serialize_lavado(t) for t in items],
    })


# ===================================================================
# SubTipos de Lavado (Interior / Exterior / Completo)
# ===================================================================
@api_publica_bp.route('/subtipos-lavado')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/subtipos-lavado', include_qs=True))
def subtipos_lavado():
    tipo_id = request.args.get('tipo_lavado_id', type=int)
    tipo_slug = request.args.get('tipo_lavado_slug', '').strip()

    query = SubTipoLavado.query.filter_by(activo=True)

    if tipo_id:
        query = query.filter(SubTipoLavado.tipo_lavado_id == tipo_id)
    elif tipo_slug:
        tl = TipoLavado.query.filter_by(slug=tipo_slug, activo=True).first()
        if tl:
            query = query.filter(SubTipoLavado.tipo_lavado_id == tl.id)
        else:
            return jsonify({
                'success': True,
                'subtipos': [],
            })

    items = query.order_by(SubTipoLavado.orden, SubTipoLavado.id).all()
    return jsonify({
        'success': True,
        'subtipos': [serialize_subtipo(s) for s in items],
    })


# ===================================================================
# Tipos de Detallado
# ===================================================================
@api_publica_bp.route('/tipos-detallado')
@cache.cached(timeout=86400, key_prefix=lambda: _view_cache_key('/api/publica/tipos-detallado'))
def tipos_detallado():
    items = TipoDetallado.query.filter_by(activo=True).order_by(
        TipoDetallado.orden, TipoDetallado.id
    ).all()
    return jsonify({
        'success': True,
        'tipos_detallado': [serialize_detallado(t) for t in items],
    })


# ===================================================================
# Consulta de Precio (motor central)
# ===================================================================
@api_publica_bp.route('/precio')
@limiter.limit("30 per minute")
def consultar_precio():
    vehiculo_slug       = request.args.get('vehiculo_slug', '').strip()
    categoria_slug      = request.args.get('categoria_slug', '').strip()
    tipo_lavado_slug    = request.args.get('tipo_lavado_slug', '').strip() or None
    subtipo_slug        = request.args.get('subtipo_slug', '').strip() or None
    tipo_detallado_slug = request.args.get('tipo_detallado_slug', '').strip() or None
    servicio_id         = request.args.get('servicio_id', type=int)

    if not vehiculo_slug or not categoria_slug:
        return jsonify({
            'success': False,
            'error': 'Parametros requeridos: vehiculo_slug, categoria_slug.',
        }), 400

    resultado, error = PricingEngine.obtener_precio(
        vehiculo_slug=vehiculo_slug,
        categoria_slug=categoria_slug,
        tipo_lavado_slug=tipo_lavado_slug,
        subtipo_slug=subtipo_slug,
        tipo_detallado_slug=tipo_detallado_slug,
        servicio_id=servicio_id,
    )

    if error:
        return jsonify({'success': False, 'error': error}), 404

    return jsonify({
        'success': True,
        'precio': resultado,
    })


# ===================================================================
# Disponibilidad Multi-dia (para Integral)
# ===================================================================
@api_publica_bp.route('/disponibilidad-multidia')
def disponibilidad_multidia():
    fecha_str   = request.args.get('fecha', '').strip()
    dias_str    = request.args.get('dias', '1')
    duracion_str = request.args.get('duracion_min', '60')

    from datetime import datetime as dt, timedelta

    if not fecha_str:
        return jsonify({'success': False, 'error': 'Parametro fecha requerido.'}), 400

    try:
        fecha = dt.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Formato de fecha invalido.'}), 400

    if not validar_fecha_futura(fecha):
        return jsonify({'success': False, 'error': 'La fecha debe ser hoy o futura.'}), 400

    try:
        dias = int(dias_str)
        duracion_min = int(duracion_str)
    except (ValueError, TypeError):
        dias = 1
        duracion_min = 60

    if dias < 1:
        dias = 1

    resultado = PlanificadorOcupacion.validar_multidia(fecha, dias, duracion_min)

    return jsonify({
        'success': True,
        'fecha_inicio': fecha_str,
        'dias': dias,
        'resultado': resultado,
    })
