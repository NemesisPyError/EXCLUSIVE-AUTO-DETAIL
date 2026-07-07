from flask import Blueprint
admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')

def _invalidar_cache():
    from extensions import invalidar_cache_prefijo
    invalidar_cache_prefijo()

from routes.admin import dashboard, reservas, servicios, horarios, galeria, clientes, factores_tiempo, usuarios
