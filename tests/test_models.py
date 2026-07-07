from models.usuario import Usuario
from models.reserva import Reserva
from extensions import db as _db
from datetime import date, time


def test_usuario_password_hash(app):
    with app.app_context():
        user = Usuario(nombre='Test', email='pass@test.com', rol='admin')
        user.set_password('Secure123!')
        assert user.password_hash != 'Secure123!'
        assert user.check_password('Secure123!') is True
        assert user.check_password('WrongPass') is False


def test_usuario_session_version(app):
    with app.app_context():
        user = Usuario(nombre='Test', email='sv@test.com', rol='admin', session_version=0)
        assert user.session_version == 0
        user.increment_session_version()
        assert user.session_version == 1
        user.increment_session_version()
        assert user.session_version == 2


def test_usuario_locked(app):
    with app.app_context():
        user = Usuario(nombre='Test', email='lock@test.com', rol='empleado', login_attempts=0)
        user.set_password('Pass1234!')
        assert user.is_locked is False
        assert user.login_attempts == 0
        for _ in range(5):
            user.record_failed_attempt()
        assert user.login_attempts == 5
        assert user.is_locked is True
        assert user.session_version == 1


def test_reserva_creation(app):
    with app.app_context():
        r = Reserva(
            cliente_id=1,
            estado_id=1,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            duracion_total_min=60,
            observaciones='Test reserva',
        )
        assert r.observaciones == 'Test reserva'
        assert r.fecha == date.today()
        assert r.hora_inicio == time(10, 0)
        assert r.duracion_total_min == 60
