import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import pytest

from config import config as _app_config


class _TestConfig(_app_config['development']):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    TESTING = True
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = 'test-csrf-secret-32chars-minimum'


_app_config['testing'] = _TestConfig


from app import create_app
from extensions import db as _db


@pytest.fixture(autouse=True)
def _patch_sqlite_with_for_update(monkeypatch):
    from sqlalchemy.orm.query import Query as SAQuery

    def _noop(self, *args, **kwargs):
        return self
    monkeypatch.setattr(SAQuery, 'with_for_update', _noop)


@pytest.fixture(autouse=True)
def _patch_limiter_rate_limit(monkeypatch):
    from flask_limiter import Limiter

    original_init = Limiter.__init__

    def _init_no_limits(self, *args, **kwargs):
        kwargs['enabled'] = False
        original_init(self, *args, **kwargs)
    monkeypatch.setattr(Limiter, '__init__', _init_no_limits)


@pytest.fixture
def app():
    app = create_app('testing')
    app.config['REDIS_URL'] = ''

    with app.app_context():
        _seed_test_data(_db)

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_test_data(db):
    from models.estado_reserva import EstadoReserva
    from models.horario import Horario
    from models.usuario import Usuario
    from models.tipo_vehiculo import TipoVehiculo
    from models.categoria_servicio import CategoriaServicio
    from models.tipo_lavado import TipoLavado
    from models.subtipo_lavado import SubTipoLavado
    from models.regla_precio import ReglaPrecio
    from datetime import time

    estados_data = [
        ('Pendiente', '#ffc107', 1), ('Confirmada', '#0d6efd', 2),
        ('Vehiculo recibido', '#17a2b8', 3), ('En proceso', '#6f42c1', 4),
        ('Lavado terminado', '#fd7e14', 5), ('Esperando retiro', '#198754', 6),
        ('Finalizada', '#0dcaf0', 7), ('Cancelada', '#dc3545', 8),
    ]
    for nombre, color, orden in estados_data:
        db.session.add(EstadoReserva(nombre=nombre, color_badge=color, orden=orden))

    for dia in range(1, 7):
        db.session.add(Horario(dia_semana=dia, hora_inicio=time(7, 0), hora_fin=time(18, 0), capacidad_maxima=3, activo=True))

    admin = Usuario(nombre='Admin Test', email='admin@test.com', rol='admin', activo=True)
    admin.set_password('Test1234!')
    db.session.add(admin)

    emp = Usuario(nombre='Empleado Test', email='empleado@test.com', rol='empleado', activo=True)
    emp.set_password('Test1234!')
    db.session.add(emp)

    tv = TipoVehiculo(nombre='Auto', slug='auto', icono='fa-car', orden=1, activo=True)
    db.session.add(tv)
    cs = CategoriaServicio(nombre='Lavado', slug='lavado', orden=1, activo=True)
    db.session.add(cs)
    tl = TipoLavado(nombre='Normal', slug='normal', orden=1, activo=True)
    db.session.add(tl)
    st = SubTipoLavado(tipo_lavado_id=1, nombre='Completo', slug='completo', orden=1, activo=True)
    db.session.add(st)

    db.session.flush()

    db.session.add(ReglaPrecio(
        categoria_servicio_id=cs.id, tipo_vehiculo_id=tv.id,
        tipo_lavado_id=tl.id, subtipo_lavado_id=st.id,
        precio_fijo=40000, tiempo_estimado_min=50, dias_bloqueo=0,
        descripcion_publica='Lavado Normal Completo', activo=True
    ))

    db.session.commit()


@pytest.fixture
def auth_client(client):
    client.post('/login', data={'email': 'admin@test.com', 'password': 'Test1234!'}, follow_redirects=False)
    return client


@pytest.fixture
def empleado_client(client):
    client.post('/login', data={'email': 'empleado@test.com', 'password': 'Test1234!'}, follow_redirects=False)
    return client
