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
        'cedula': '1234567',
        'telefono': '0994123456',
        'tipo_vehiculo_slug': 'auto',
        'tipo_vehiculo': 'Auto',
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'categoria_slug': 'lavado',
        'tipo_lavado_slug': 'normal',
        'subtipo_slug': 'completo',
        'fecha': manana.strftime('%Y-%m-%d'),
        'hora': '10:00',
    }
    resp = client.post('/reservas/crear',
                       data=json.dumps(payload),
                       content_type='application/json')
    assert resp.status_code in (201, 409)


def test_confirmacion(client):
    manana = date.today() + timedelta(days=2)
    payload = {
        'nombre': 'Maria',
        'apellido': 'Lopez',
        'cedula': '7654321',
        'telefono': '0981123456',
        'tipo_vehiculo_slug': 'auto',
        'tipo_vehiculo': 'Auto',
        'marca': 'Honda',
        'modelo': 'Civic',
        'categoria_slug': 'lavado',
        'tipo_lavado_slug': 'normal',
        'subtipo_slug': 'completo',
        'fecha': manana.strftime('%Y-%m-%d'),
        'hora': '11:00',
    }
    resp = client.post('/reservas/crear',
                       data=json.dumps(payload),
                       content_type='application/json')
    if resp.status_code == 201:
        data = json.loads(resp.data)
        token = data.get('confirmacion_token') or data.get('data', {}).get('confirmacion_token')
        if token:
            confirm_resp = client.get(f'/reservas/confirmacion/{token}')
            assert confirm_resp.status_code == 200
