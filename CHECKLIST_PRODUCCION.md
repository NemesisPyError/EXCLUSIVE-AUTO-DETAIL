# Checklist de Preparación para Producción

## 1. Variables de Entorno (.env)

- [ ] `SECRET_KEY` — string aleatorio de al menos 32 caracteres. Generar con: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `FLASK_ENV=production`
- [ ] `REDIS_URL` — obligatorio en producción. Ej: `redis://redis:6379/0`
- [ ] `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` — credenciales MySQL
- [ ] `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SENDER` — SMTP config
- [ ] `PROXY_COUNT=1` — si usás Nginx delante. Con Cloudflare + Nginx: `PROXY_COUNT=2`

## 2. Infraestructura

- [ ] MySQL 8.0 instalado y accesible desde el container/VPS
- [ ] Redis 7 instalado y corriendo
- [ ] Nginx configurado como reverse proxy delante de Gunicorn
- [ ] Certificado SSL (Let's Encrypt) instalado
- [ ] Puerto 443 abierto, puerto 80 redirige a 443
- [ ] Firewall: solo puertos 22, 80, 443 abiertos al público

## 3. Docker

- [ ] `docker-compose up -d` arranca los 3 servicios (app, mysql, redis)
- [ ] Volúmenes persistentes para MySQL y Redis
- [ ] Healthcheck funcionando en los 3 servicios
- [ ] Usuario no-root en el container de la app
- [ ] `restart: unless-stopped` en todos los servicios
- [ ] `.env` copiado y configurado antes del deploy

## 4. Nginx (ejemplo de configuración)

```nginx
server {
    listen 443 ssl;
    server_name tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }

    location /static/ {
        alias /ruta/al/proyecto/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

- [ ] `PROXY_COUNT=1` en .env (1 proxy: Nginx)
- [ ] Gunicorn configurado con `--forwarded-allow-ips="*"` o IP de Nginx

## 5. Gunicorn

- [ ] Ejecutando con 4 workers: `gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'`
- [ ] Timeout configurado (mínimo 30s para uploads de imágenes)
- [ ] Logging a archivo o stdout/stderr capturado por Docker

## 6. Base de Datos

- [ ] `python seed.py` ejecutado para datos iniciales
- [ ] Usuario admin creado (cambiar contraseña por defecto inmediatamente)
- [ ] Índices creados automáticamente en startup (10 índices)

## 7. Seguridad

- [ ] `DEBUG=False` (ProductionConfig)
- [ ] `SESSION_COOKIE_SECURE=True` (cookies solo por HTTPS)
- [ ] `SESSION_COOKIE_HTTPONLY=True`
- [ ] `SESSION_COOKIE_SAMESITE='Lax'`
- [ ] `REMEMBER_COOKIE_SECURE=True`
- [ ] Redis corriendo (rate limiting compartido entre workers)
- [ ] CSP configurado (unsafe-inline documentado como excepción necesaria)
- [ ] HSTS activo en producción (max-age=31536000)
- [ ] Contraseña del admin cambiada de `Admin1234!`

## 8. Monitoreo

- [ ] `/api/health` responde 200
- [ ] Logs visibles via `docker-compose logs -f app`
- [ ] Rate limiting no bloquea tráfico legítimo (monitorear logs)
- [ ] SMTP funcional: probar recuperación de contraseña

## 9. Backup

- [ ] Backup diario de MySQL configurado (cron o similar)
- [ ] Volumen de datos MySQL fuera del container
- [ ] Plan de restauración documentado

---

## Puntuación de preparación: 9/10

Sistema preparado para producción con:
- Configuración de seguridad completa (8 headers HTTP, RBAC, CSRF, rate limiting)
- Rate limiting y caché compartidos entre workers (Redis)
- ProxyFix para IPs reales detrás de Nginx
- SMTP con reintentos para recuperación de contraseña
- Docker con healthchecks y volúmenes persistentes

Riesgos residuales:
- CSP `unsafe-inline` en wizard.js y admin CRUDs (requiere migración de JS inline a archivos externos, ~1400 líneas)
- Sin sistema de backups automático integrado (usar cron/VPS tools)
