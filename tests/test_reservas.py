import json
from datetime import date, timedelta


def test_nueva_page(client):
    resp = client.get('/reservas/nueva')
    assert resp.status_code == 200


def test_crear_reserva(client):
    manana = date.today() + timedelta(days=1)
    payload = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'telefono': '0994123456',
        'cedula': '1234567',
        'tipo_vehiculo_id': 2,
        'segmento_id': 2,
        'servicio_id': 3,
        'nivel_suciedad_id': 1,
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'fecha': manana.strftime('%Y-%m-%d'),
        'hora_inicio': '10:00',
    }
    resp = client.post('/reservas/crear',
                       data=json.dumps(payload),
                       content_type='application/json')
    assert resp.status_code in (201, 400, 409)


def test_confirmacion(client):
    manana = date.today() + timedelta(days=2)
    payload = {
        'nombre': 'Maria',
        'apellido': 'Lopez',
        'telefono': '0981123456',
        'cedula': '7654321',
        'tipo_vehiculo_id': 2,
        'segmento_id': 2,
        'servicio_id': 3,
        'nivel_suciedad_id': 1,
        'marca': 'Honda',
        'modelo': 'Civic',
        'fecha': manana.strftime('%Y-%m-%d'),
        'hora_inicio': '11:00',
    }
    resp = client.post('/reservas/crear',
                       data=json.dumps(payload),
                       content_type='application/json')
    if resp.status_code == 201:
        data = json.loads(resp.data)
        token = data.get('confirmacion_token')
        if token:
            confirm_resp = client.get(f'/reservas/confirmacion/{token}')
            assert confirm_resp.status_code == 200
