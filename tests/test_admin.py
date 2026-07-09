def test_dashboard_redirects_when_not_logged(client):
    resp = client.get('/admin/dashboard', follow_redirects=False)
    assert resp.status_code == 302


def test_dashboard_auth(auth_client):
    resp = auth_client.get('/admin/dashboard')
    assert resp.status_code == 200


def test_reservas_list(auth_client):
    resp = auth_client.get('/admin/reservas')
    assert resp.status_code == 200


def test_servicios_list(auth_client):
    resp = auth_client.get('/admin/servicios')
    assert resp.status_code == 200


def test_clientes_list(auth_client):
    resp = auth_client.get('/admin/clientes')
    assert resp.status_code == 200


def test_horarios_list(auth_client):
    resp = auth_client.get('/admin/horarios')
    assert resp.status_code == 200


def test_galeria_list(auth_client):
    resp = auth_client.get('/admin/galeria')
    assert resp.status_code == 200


def test_usuarios_list(auth_client):
    resp = auth_client.get('/admin/usuarios')
    assert resp.status_code == 200


def test_empleado_cannot_access_servicios(empleado_client):
    resp = empleado_client.get('/admin/servicios', follow_redirects=False)
    assert resp.status_code in (302, 403)
