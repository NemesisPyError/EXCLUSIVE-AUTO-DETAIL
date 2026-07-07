from flask import Blueprint, render_template, request, jsonify
from extensions import db, limiter, csrf
from models.reserva import Reserva
from services.reservation_builder import ReservationBuilder

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/nueva')
def nueva():
    return render_template('reservas/nueva.html')


@reservas_bp.route('/crear', methods=['POST'])
@limiter.limit("15 per minute", error_message='Demasiadas solicitudes. Intente de nuevo en un minuto.')
@csrf.exempt
def crear():
    data = request.get_json(silent=True)
    success, result, http_status = ReservationBuilder.build_reservation(data)
    return jsonify({'success': success, **result}), http_status


@reservas_bp.route('/confirmacion/<token>')
def confirmacion(token):
    reserva = Reserva.query.filter_by(confirmacion_token=token).first_or_404()
    return render_template('reservas/confirmacion.html', reserva=reserva)
