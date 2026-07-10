# Checklist de Produccion — Exclusive Auto Detail

## 1. Variables de Entorno (.env)

- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY` — generar con `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT=5432`, `DB_NAME`
- [ ] `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db`
- [ ] `REDIS_URL=redis://redis:6379/0` (obligatorio en produccion)
- [ ] `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SENDER`
- [ ] `PROXY_COUNT=1` (si hay Nginx delante)

## 2. Infraestructura

- [ ] PostgreSQL 16 instalado y accesible
- [ ] Redis 7 instalado y accesible
- [ ] Nginx configurado como proxy reverso
- [ ] SSL/TLS (Let's Encrypt o comercial)
- [ ] Firewall: solo puertos 80/443 abiertos

## 3. Base de Datos

- [ ] Crear base de datos: `createdb exclusive_autodetail`
- [ ] Ejecutar migraciones: `flask db upgrade`
- [ ] Sembrar datos: `python seed.py`
- [ ] Cambiar contraseña del admin en el panel

## 4. Docker

- [ ] Revisar docker-compose.yml (volumenes, healthchecks)
- [ ] `docker-compose up -d`
- [ ] `docker-compose exec app flask db upgrade`
- [ ] `docker-compose exec app python seed.py`

## 5. Nginx (ejemplo)

```nginx
server {
    listen 80;
    server_name exclusiveautodetail.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name exclusiveautodetail.com;

    ssl_certificate /etc/letsencrypt/live/.../fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/.../privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6. Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --forwarded-allow-ips="*" "app:create_app()"
```

## 7. Seguridad

- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `SESSION_COOKIE_HTTPONLY=True`
- [ ] `SESSION_COOKIE_SAMESITE='Lax'`
- [ ] `REMEMBER_COOKIE_SECURE=True`
- [ ] CSP, HSTS, X-Frame-Options configurados en middlewares.py
- [ ] Rate limiting activo (Flask-Limiter con Redis)
- [ ] Admin password cambiada

## 8. Monitoreo

- [ ] Health check: `GET /api/health`
- [ ] Logs de Gunicorn con rotacion
- [ ] Monitoreo de Redis (memoria, conexiones)

## 9. Backup

- [ ] Backup diario de PostgreSQL: `pg_dump exclusive_autodetail > backup.sql`
- [ ] Backup de imagenes subidas (static/img/)
- [ ] Probar restauracion de backup

## 10. Migraciones

- [ ] Las migraciones se ejecutan como parte del deploy
- [ ] No se usa `db.create_all()` en produccion
- [ ] `flask db upgrade` como paso previo al inicio de la app
