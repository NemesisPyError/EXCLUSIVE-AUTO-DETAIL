import os
import sys
import logging
from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config
from extensions import db, login_manager, csrf, limiter, cache

logger = logging.getLogger(__name__)


def _setup_proxy(app):
    proxy_count = app.config.get('PROXY_COUNT', 0)
    if proxy_count > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxy_count, x_proto=proxy_count, x_host=0, x_port=0)
        logger.info('ProxyFix activado con x_for=x_proto=%d', proxy_count)


def _setup_logging(app):
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    _setup_logging(app)
    _setup_proxy(app)

    if config_name == 'production' and not os.getenv('REDIS_URL'):
        logger.critical(
            'REDIS_URL no definida. En produccion Redis es obligatorio para '
            'rate limiting compartido y cache entre workers Gunicorn.'
        )
        sys.exit(1)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'

    from middlewares import register_session_check, register_security_headers
    register_session_check(app)
    register_security_headers(app)

    from template_helpers import register_template_helpers
    register_template_helpers(app)

    from routes import main_bp, auth_bp, admin_bp, reservas_bp, api_bp, webhooks_bp, api_publica_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reservas_bp, url_prefix='/reservas')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_publica_bp, url_prefix='/api/publica')
    app.register_blueprint(webhooks_bp, url_prefix='/webhooks')

    with app.app_context():
        import models
        db.create_all()
        from database.migrations import migrar_galeria_categorias, asegurar_esquema, _migrar_estados_cambio
        migrar_galeria_categorias()
        asegurar_esquema()
        _migrar_estados_cambio()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
