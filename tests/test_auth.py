from tests.conftest import _seed_test_data  # noqa: F401 - referenced by conftest


def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_invalid(client):
    resp = client.post('/login', data={
        'email': 'admin@test.com', 'password': 'WrongPass!',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'danger' in resp.data or b'incorrectos' in resp.data.lower()


def test_login_valid(client):
    resp = client.post('/login', data={
        'email': 'admin@test.com', 'password': 'Test1234!',
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert '/admin/dashboard' in resp.headers.get('Location', '')


def test_logout(auth_client):
    resp = auth_client.get('/logout', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '') or '/' in resp.headers.get('Location', '')


def test_forgot_password_page(client):
    resp = client.get('/forgot-password')
    assert resp.status_code == 200


def test_forgot_password_post(client):
    resp = client.post('/forgot-password', data={
        'email': 'admin@test.com',
    }, follow_redirects=True)
    assert resp.status_code == 200
    data = resp.data.decode('utf-8').lower()
    assert 'registrado' in data or 'recibira' in data
