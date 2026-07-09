import os
import pytest

from config import config as _app_config
from config import TestConfig

_app_config['testing'] = TestConfig

from app import create_app
from extensions import db as _db


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
        _db.create_all()
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
    from models.segmento import Segmento
    from models.tipo_vehiculo import TipoVehiculo
    from models.nivel_suciedad import NivelSuciedad
    from models.categoria_servicio import CategoriaServicio
    from models.servicio import Servicio
    from models.precio_servicio import PrecioServicio
    from models.box import Box
    from models.tipo_box import TipoBox
    from datetime import time

    estados_data = [
        ('Pendiente', '#6c757d', 1, False, False),
        ('Confirmada', '#0d6efd', 2, False, False),
        ('Recibida', '#198754', 3, False, False),
        ('En Proceso', '#fd7e14', 4, False, False),
        ('Lista', '#0dcaf0', 5, False, False),
        ('Entregada', '#198754', 6, True, False),
        ('Cancelada', '#dc3545', 7, True, True),
    ]
    for nombre, color, orden, terminal, cancel in estados_data:
        db.session.add(EstadoReserva(
            nombre=nombre, color_badge=color, orden=orden,
            es_terminal=terminal, es_cancelacion=cancel,
        ))

    for dia in range(1, 7):
        db.session.add(Horario(
            dia_semana=dia, hora_inicio=time(7, 0),
            hora_fin=time(18, 0), activo=True,
        ))

    admin = Usuario(
        nombre='Admin', apellido='Test',
        email='admin@test.com', rol='admin', activo=True,
    )
    admin.set_password('Test1234!')
    db.session.add(admin)

    emp = Usuario(
        nombre='Empleado', apellido='Test',
        email='empleado@test.com', rol='empleado', activo=True,
    )
    emp.set_password('Test1234!')
    db.session.add(emp)

    seg = Segmento(nombre='Mediano', slug='mediano', orden=2)
    db.session.add(seg)
    tv = TipoVehiculo(nombre='Auto', slug='auto', icono='fa-car', orden=2)
    db.session.add(tv)
    nv = NivelSuciedad(nombre='Normal', orden=1)
    db.session.add(nv)
    cat = CategoriaServicio(nombre='Lavado', slug='lavado', orden=1)
    db.session.add(cat)

    db.session.flush()

    svc = Servicio(
        nombre='Lavado Completo', slug='lavado-completo',
        tipo='base', categoria_servicio_id=cat.id,
    )
    db.session.add(svc)
    db.session.flush()

    db.session.add(PrecioServicio(
        servicio_id=svc.id,
        tipo_vehiculo_id=tv.id,
        segmento_id=seg.id,
        nivel_suciedad_id=nv.id,
        precio=40000,
        duracion_minutos=50,
    ))

    tb = TipoBox(nombre='Estandar')
    db.session.add(tb)
    db.session.flush()
    db.session.add(Box(tipo_box_id=tb.id, nombre='Box 1', activo=True, orden=1))

    db.session.commit()


@pytest.fixture
def auth_client(client):
    client.post('/login', data={
        'email': 'admin@test.com',
        'password': 'Test1234!',
    }, follow_redirects=False)
    return client


@pytest.fixture
def empleado_client(client):
    client.post('/login', data={
        'email': 'empleado@test.com',
        'password': 'Test1234!',
    }, follow_redirects=False)
    return client
