"""
Webhooks — Integración con servicios externos.
"""
from flask import Blueprint, jsonify

webhooks_bp = Blueprint('webhooks', __name__)


@webhooks_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'service': 'webhooks',
        'status': 'inactive',
        'message': 'Webhooks no implementados aún.'
    })
