from flask import Blueprint, render_template, request, jsonify
from extensions import db, limiter, csrf
from models.reserva import Reserva
from services.reservation_builder import ReservationBuilder, ReservationValidationError

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/nueva')
def nueva():
    return render_template('reservas/nueva.html')


@reservas_bp.route('/crear', methods=['POST'])
@limiter.limit("15 per minute", error_message='Demasiadas solicitudes. Intente de nuevo en un minuto.')
@csrf.exempt
def crear():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Datos invalidos.'}), 400

    try:
        reserva = ReservationBuilder.build_reservation(data)
        return jsonify({
            'success': True,
            'reserva_id': reserva.id,
            'confirmacion_token': reserva.confirmacion_token,
        }), 201
    except ReservationValidationError as e:
        return jsonify({'success': False, 'errors': e.args[0]}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reservas_bp.route('/confirmacion/<token>')
def confirmacion(token):
    reserva = Reserva.query.filter_by(confirmacion_token=token).first_or_404()
    return render_template('reservas/confirmacion.html', reserva=reserva)
