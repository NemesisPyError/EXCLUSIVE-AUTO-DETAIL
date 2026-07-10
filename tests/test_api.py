import json


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
    assert 'categorias' in data


def test_segmentos(client):
    resp = client.get('/api/publica/segmentos')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('success') is True


def test_niveles_suciedad(client):
    resp = client.get('/api/publica/niveles-suciedad')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('success') is True


def test_precio(client):
    resp = client.get('/api/publica/precio', query_string={
        'servicio_id': 1,
        'tipo_vehiculo_id': 2,
        'segmento_id': 2,
        'nivel_suciedad_id': 1,
    })
    assert resp.status_code in (200, 404)


def test_precio_invalid(client):
    resp = client.get('/api/publica/precio')
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert data.get('success') is False


def test_servicios(client):
    resp = client.get('/api/publica/servicios')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('success') is True


def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('status') == 'ok'
