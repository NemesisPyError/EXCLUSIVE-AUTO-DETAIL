import json
from datetime import date, timedelta


def test_tipos_vehiculo(client):
    resp = client.get('/api/publica/tipos-vehiculo')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('success') is True
    assert 'tipos_vehiculo' in data


def test_categorias(client):
    resp = client.get('/api/publica/categorias-servicio')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('success') is True


def test_precio(client):
    resp = client.get('/api/publica/precio', query_string={
        'vehiculo_slug': 'auto',
        'categoria_slug': 'lavado',
    })
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('success') is True


def test_precio_invalid(client):
    resp = client.get('/api/publica/precio')
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert data.get('success') is False


def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('status') == 'ok'
