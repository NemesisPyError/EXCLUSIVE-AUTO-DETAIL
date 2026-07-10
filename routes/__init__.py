from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp
from routes.webhooks import webhooks_bp
from routes.api_routes import api_publica_bp

from flask import Blueprint

api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health():
    from flask import jsonify
    return jsonify({
        'status': 'ok',
        'message': 'Exclusive Auto Detail API funcionando'
    })
