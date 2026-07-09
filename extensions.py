import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

_redis_url = os.getenv('REDIS_URL')
if _redis_url:
    _storage = _redis_url
else:
    _storage = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute", "30 per second"],
    storage_uri=_storage,
)

cache = Cache()


def _view_cache_key(path, include_qs=False):
    from flask import request
    epoch = cache.get('catalog:epoch') or 0
    key = f'catalog/v{epoch}{path}'
    if include_qs:
        import hashlib
        qs = request.query_string.decode()
        if qs:
            key = f'{key}/{hashlib.md5(qs.encode()).hexdigest()[:8]}'
    return key


def invalidar_cache_prefijo(pattern=None):
    if pattern is None or pattern == 'precio':
        from services.pricing_service import PricingEngine
        PricingEngine.invalidar_cache_precio()

    if pattern is None or pattern == 'catalogo':
        cache.set('catalog:epoch', (cache.get('catalog:epoch') or 0) + 1)
