import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

print("DATABASE_URL env:", os.getenv('DATABASE_URL'))
print("DB_USER:", os.getenv('DB_USER'))
print("DB_PASSWORD:", os.getenv('DB_PASSWORD'))

_DEFAULT_SECRET = os.getenv('SECRET_KEY')
if not _DEFAULT_SECRET:
    _DEFAULT_SECRET = os.getenv('FLASK_SECRET_KEY')

_has_redis = bool(os.getenv('REDIS_URL'))


class Config:
    SECRET_KEY = _DEFAULT_SECRET or secrets.token_hex(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = 3600
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'static', 'img'
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = False

    REDIS_URL = os.getenv('REDIS_URL', '')

    PROXY_COUNT = int(os.getenv('PROXY_COUNT', 0))

    CACHE_TYPE = 'RedisCache' if _has_redis else 'SimpleCache'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', '')
    CACHE_KEY_PREFIX = 'exclusive_autodetail:'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_OPTIONS = {'threshold': 500} if not _has_redis else {}


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER', 'exclusive_user')}:"
        f"{os.getenv('DB_PASSWORD', 'secure_password')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'exclusive_autodetail')}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
    }


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = 'test-csrf-secret-32chars-minimum'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql+psycopg2:///exclusive_autodetail_test'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
