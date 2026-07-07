import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

load_dotenv()

db = SQLAlchemy()
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
    """Genera clave versionada para @cache.cached en vistas de catalogo.
    Incluye catalog:epoch para que invalidar_cache_prefijo() pueda
    invalidar todas sin flushdb. El prefijo CACHE_KEY_PREFIX de config.py
    se agrega automaticamente por Flask-Caching."""
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
    """Invalida datos cacheados sin flushdb ni clear() global.
    Funciona con RedisCache y SimpleCache: incrementa contadores de version;
    las entradas huerfanas expiran via TTL (Redis) o se evictan por
    limite de entradas (SimpleCache threshold=500).

    Args:
        pattern: None (todo), 'precio', 'catalogo'
    """
    if pattern is None or pattern == 'precio':
        from services.pricing_service import PricingEngine
        PricingEngine.invalidar_cache_precio()

    if pattern is None or pattern == 'catalogo':
        cache.set('catalog:epoch', (cache.get('catalog:epoch') or 0) + 1)
