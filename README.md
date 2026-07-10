# Exclusive Auto Detail — Sistema de Gestion de Detailing Automotriz

Sistema web de reservas para un taller de detailing automotriz en Paraguay.

## Stack Tecnologico

| Capa | Tecnologia |
|------|-----------|
| Backend | Python 3.12, Flask 3.1 |
| ORM | SQLAlchemy 2.0 (Declarative Models) |
| Base de datos | PostgreSQL 16 |
| Migraciones | Alembic (Flask-Migrate) |
| Cache | Redis 7 (prod) / SimpleCache (dev) |
| Frontend | Jinja2 + Bootstrap 5 + Vanilla JS |
| Autenticacion | Flask-Login + bcrypt |
| Rate Limiting | Flask-Limiter |
| Server | Gunicorn 23 |
| Contenedores | Docker + docker-compose |

## Inicio Rapido

```bash
# 1. Clonar y crear .env
cp .env.example .env
# Editar .env con las credenciales de PostgreSQL

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear base de datos PostgreSQL
createdb exclusive_autodetail

# 4. Ejecutar migraciones
flask db upgrade

# 5. Sembrar datos iniciales
python seed.py

# 6. Ejecutar
flask run
# Admin: admin@exclusiveautodetail.com / Admin1234!
```

## Docker

```bash
docker-compose up -d
docker-compose exec app flask db upgrade
docker-compose exec app python seed.py
```

## Variables de Entorno

Ver `.env.example` para todas las variables. Principales:

| Variable | Descripcion |
|----------|-------------|
| `FLASK_ENV` | `development`, `testing`, `production` |
| `SECRET_KEY` | Clave secreta de Flask |
| `DB_USER` | Usuario PostgreSQL |
| `DB_PASSWORD` | Contrasena PostgreSQL |
| `DB_HOST` | Host PostgreSQL |
| `DB_PORT` | Puerto PostgreSQL (5432) |
| `DB_NAME` | Nombre de la base de datos |
| `DATABASE_URL` | URL completa PostgreSQL (alternativa) |
| `REDIS_URL` | URL de Redis (obligatorio en prod) |

## Migraciones

```bash
# Generar migracion tras cambiar modelos
flask db migrate -m "descripcion del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir ultima migracion
flask db downgrade
```

## Tests

```bash
pytest
```

## Estructura del Proyecto

```
├── app.py                    # Application factory
├── config.py                 # Configuracion por entorno
├── extensions.py             # Extensiones Flask
├── decorators.py             # Decoradores (@role_required)
├── middlewares.py            # Seguridad y sesiones
├── template_helpers.py       # Filtros y context processors Jinja2
├── seed.py                   # Datos iniciales
├── alembic.ini               # Configuracion Alembic
├── migrations/               # Migraciones
├── models/                   # 26 modelos SQLAlchemy
├── services/                 # Logica de negocio
├── routes/                   # Blueprints y controladores
├── templates/                # Vistas Jinja2
├── static/                   # CSS, JS, imagenes
└── tests/                    # Tests pytest
```
