from flask import Blueprint, render_template, jsonify, request
import json
from models.servicio import Servicio
from models.galeria import Galeria
from models.galeria_categoria import GaleriaCategoria
from models.testimonio import Testimonio
from models.horario import Horario
from models.reserva import Reserva
from models.factor_tiempo import FactorTiempo
from services.validaciones import validar_fecha_futura
from services.duracion import PlanificadorOcupacion
from extensions import cache, _view_cache_key

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    from sqlalchemy.orm import joinedload
    categorias = GaleriaCategoria.query.options(
        joinedload(GaleriaCategoria.imagenes)
    ).filter_by(
        activo=True
    ).order_by(GaleriaCategoria.orden, GaleriaCategoria.id).all()

    galeria_categorias = []
    galeria_json = {}
    for cat in categorias:
        imgs = [i for i in cat.imagenes if i.activo]
        imgs.sort(key=lambda x: (x.orden, x.id))
        if not imgs:
            continue
        galeria_categorias.append({'tipo': cat.nombre, 'imagenes': imgs})
        galeria_json[cat.nombre] = [
            {
                'url': img.url_imagen,
                'thumb': img.url_thumb or img.url_imagen,
                'titulo': img.titulo,
                'descripcion': img.descripcion or '',
            }
            for img in imgs
        ]

    return render_template(
        'index.html',
        galeria_categorias=galeria_categorias,
        galeria_json=json.dumps(galeria_json, ensure_ascii=False),
    )


@main_bp.route('/servicios')
def servicios():
    lista = Servicio.query.filter_by(
        activo=True
    ).order_by(Servicio.categoria, Servicio.nombre).all()
    return render_template('servicios.html', servicios=lista)


@main_bp.route('/galeria')
def galeria():
    imagenes = Galeria.query.filter_by(
        activo=True
    ).order_by(Galeria.orden).all()
    return render_template('galeria.html', galeria=imagenes)


@main_bp.route('/testimonios')
def testimonios():
    items = Testimonio.query.filter_by(
        activo=True
    ).order_by(Testimonio.created_at.desc()).all()
    return render_template('testimonios.html', testimonios=items)


@main_bp.route('/contacto')
def contacto():
    return render_template('contacto.html')


@main_bp.route('/servicios-json')
def servicios_json():
    lista = Servicio.query.filter_by(
        activo=True
    ).order_by(Servicio.categoria, Servicio.nombre).all()
    return jsonify([{
        'id': s.id,
        'nombre': s.nombre,
        'descripcion': s.descripcion,
        'categoria': s.categoria,
        'precio': float(s.precio),
        'tiempo_estimado_min': s.tiempo_estimado_min,
        'tiempo_estimado': s.tiempo_estimado_formateado,
    } for s in lista])


@main_bp.route('/horarios-disponibles')
@cache.cached(timeout=1800, key_prefix=lambda: _view_cache_key('/horarios-disponibles', include_qs=True))
def horarios_disponibles():
    fecha_str = request.args.get('fecha')
    duracion_min_str = request.args.get('duracion_min', '')
    if not fecha_str:
        return jsonify({'success': False, 'error': 'Parametro fecha requerido (YYYY-MM-DD).'}), 400

    from datetime import datetime as dt
    try:
        fecha = dt.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Formato de fecha invalido. Use YYYY-MM-DD.'}), 400

    if not validar_fecha_futura(fecha):
        return jsonify({'success': False, 'error': 'La fecha debe ser hoy o futura.'}), 400

    try:
        duracion_min = int(duracion_min_str) if duracion_min_str else 60
    except (ValueError, TypeError):
        duracion_min = 60

    dia = fecha.weekday() + 1
    horario = Horario.query.filter_by(
        dia_semana=dia, activo=True
    ).first()

    if not horario:
        return jsonify({'success': False, 'error': 'No hay horarios disponibles para esta fecha.'}), 404

    slots = PlanificadorOcupacion.slots_disponibles(fecha, duracion_min)

    return jsonify({
        'success': True,
        'fecha': fecha_str,
        'duracion_considerada_min': duracion_min,
        'horarios': slots,
    })


@main_bp.route('/factores-tiempo-json')
@cache.cached(timeout=3600, key_prefix=lambda: _view_cache_key('/factores-tiempo-json', include_qs=True))
def factores_tiempo_json():
    tipo = request.args.get('tipo', '').strip()
    query = FactorTiempo.query.filter_by(activo=True)
    if tipo:
        query = query.filter_by(tipo=tipo)
    factores = query.order_by(FactorTiempo.tipo, FactorTiempo.orden, FactorTiempo.nombre).all()

    agrupados = {}
    for f in factores:
        if f.tipo not in agrupados:
            agrupados[f.tipo] = []
        agrupados[f.tipo].append({
            'id': f.id,
            'nombre': f.nombre,
            'minutos_adicionales': f.minutos_adicionales,
        })

    return jsonify({'success': True, 'factores': agrupados})
