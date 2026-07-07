# Exclusive Auto Detail

Sistema de reservas y gestión para un taller de detallado y lavado de vehículos en Paraguay. Reservas en línea con wizard paso a paso, pricing engine multi-categoría, panel de administración completo y notificaciones.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.1 |
| ORM | SQLAlchemy 2.0, Flask-SQLAlchemy |
| Database | MySQL 8.0 |
| Auth | Flask-Login, bcrypt |
| Forms / CSRF | Flask-WTF |
| Rate Limiting | Flask-Limiter |
| Caching | Flask-Caching (Redis / SimpleCache) |
| Frontend | Jinja2, Bootstrap 5, Vanilla JS |
| Server | Gunicorn 23 |
| Containerization | Docker, docker-compose |
| Image Processing | Pillow 12 |

## Quick Start

### 1. Clone & configure environment

```bash
git clone <repo-url> exclusive-auto-detail
cd exclusive-auto-detail
cp .env.example .env
# Edit .env with your MySQL credentials and a SECRET_KEY
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed the database

```bash
python seed.py
```

### 4. Run the app

```bash
python app.py
```

The app is now available at `http://localhost:5000`.

## Environment Variables

All variables are defined in `.env.example`:

| Variable | Required | Default | Description |
|---|---|---|---|
| `FLASK_ENV` | No | `development` | `development` or `production` |
| `SECRET_KEY` | Yes | — | Flask secret key (also reads `FLASK_SECRET_KEY` as fallback) |
| `DB_USER` | Yes | — | MySQL username |
| `DB_PASSWORD` | Yes | — | MySQL password |
| `DB_HOST` | Yes | — | MySQL host address |
| `DB_PORT` | No | `3306` | MySQL port |
| `DB_NAME` | Yes | — | MySQL database name |
| `REDIS_URL` | No | — | Redis connection string (e.g. `redis://localhost:6379/0`). Falls back to in-memory cache. |
| `MAIL_SERVER` | No | `smtp.gmail.com` | SMTP host |
| `MAIL_PORT` | No | `587` | SMTP port |
| `MAIL_USERNAME` | No | — | SMTP username |
| `MAIL_PASSWORD` | No | — | SMTP password |
| `MAIL_SENDER` | No | `noreply@exclusiveautodetail.com` | From address |
| `MAIL_USE_TLS` | No | `true` | Enable STARTTLS |

## Project Structure

```
EXCLUSIVE-AUTO-DETAIL-main/
├── app.py                  # Application factory (create_app)
├── config.py               # Configuration classes (dev / prod)
├── extensions.py           # Flask extensions init & cache helpers
├── decorators.py           # @role_required decorator
├── middlewares.py          # Session version check, security headers (CSP, HSTS)
├── template_helpers.py     # Jinja2 context processors & filters
├── seed.py                 # Database seeder
├── requirements.txt        # Python dependencies
├── Dockerfile              # Multi-stage production image
├── docker-compose.yml      # App + MySQL + Redis stack
├── models/
│   ├── usuario.py          # Admin/staff user (lockout, reset token)
│   ├── cliente.py          # Customer
│   ├── vehiculo.py         # Vehicle record
│   ├── reserva.py          # Reservation header
│   ├── reserva_item.py     # Reservation line items
│   ├── estado_reserva.py   # Reservation status (workflow states)
│   ├── estado_cambio.py    # Status change audit log
│   ├── servicio.py         # Legacy service catalog
│   ├── horario.py          # Weekly schedule (day, time range, capacity)
│   ├── galeria.py          # Gallery images
│   ├── galeria_categoria.py # Gallery categories
│   ├── testimonio.py       # Customer testimonials
│   ├── factor_tiempo.py    # Time factors (dirt level, conditions)
│   ├── tipo_vehiculo.py    # Vehicle types (auto, SUV, moto)
│   ├── categoria_servicio.py # Service categories (lavado, detallado, etc.)
│   ├── tipo_lavado.py      # Wash types (normal, alta, extrema)
│   ├── subtipo_lavado.py   # Wash subtypes (interior, exterior, completo)
│   ├── tipo_detallado.py   # Detailing types
│   └── regla_precio.py     # Price matrix rules
├── routes/
│   ├── main.py             # Public pages & JSON endpoints
│   ├── auth.py             # Login, logout, password reset
│   ├── reservas.py         # Booking wizard & creation
│   ├── api_routes.py       # Public REST API
│   ├── webhooks.py         # External webhook stubs
│   └── admin/              # Admin panel blueprints
│       ├── dashboard.py    # Dashboard with KPIs
│       ├── reservas.py     # Reservation CRUD & workflow
│       ├── servicios.py    # Service & pricing management
│       ├── horarios.py     # Schedule config
│       ├── galeria.py      # Gallery management
│       ├── clientes.py     # Customer records
│       ├── factores_tiempo.py # Time factor config
│       └── usuarios.py     # User management
├── services/
│   ├── pricing_service.py  # PricingEngine — price lookup with cache
│   ├── reservation_builder.py # ReservationBuilder — validate & persist
│   ├── duracion.py         # Duration calculator & slot planner
│   ├── validaciones.py     # Field validators (phone, date, availability)
│   ├── security_service.py # Structured security logging
│   ├── email_service.py    # SMTP email sender
│   ├── pdf_service.py      # PDF generation
│   ├── image_service.py    # Image upload & resize
│   ├── serializers.py      # Model → JSON serializers
│   └── whatsapp_service.py # Phone normalization & message templates
├── templates/
│   ├── base.html           # Base layout (Bootstrap 5)
│   ├── index.html           # Landing page
│   ├── login.html           # Admin login
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── admin/               # Admin panel templates
│   └── reservas/            # Booking wizard templates
└── static/
    ├── css/                 # Custom stylesheets
    ├── js/                  # Client-side JavaScript
    └── img/                 # Uploaded images
```

## Architecture

### Application Factory

`app.py` exports `create_app(config_name)` — creates a Flask instance, loads config from `config.py`, initializes all extensions, registers blueprints, sets up middleware, and auto-creates database tables + runs migrations on first request.

### Blueprints

| Blueprint | Prefix | Purpose |
|---|---|---|
| `main_bp` | `/` | Public pages, JSON endpoints for Slots & Factors |
| `auth_bp` | `/` | Login, logout, password reset |
| `admin_bp` | `/admin` | Full admin panel (CRUD for all entities) |
| `reservas_bp` | `/reservas` | Booking wizard UI + creation endpoint |
| `api_publica_bp` | `/api/publica` | Catalog & pricing REST API |
| `api_bp` | `/api` | Internal API + health check |
| `webhooks_bp` | `/webhooks` | External webhook receivers |

### Services Layer

Business logic lives in `services/`:

- **PricingEngine** (`pricing_service.py`) — Resolves price matrices with cache-versioned invalidation. Looks up `ReglaPrecio` by vehicle type, category, wash type, subtype, and detailing type.
- **ReservationBuilder** (`reservation_builder.py`) — Validates input, checks availability, creates customer/vehicle/reservation records, applies pricing, and assigns confirmation tokens in a single transaction.
- **CalculadorDuracion** / **PlanificadorOcupacion** (`duracion.py`) — Computes total duration from services + time factors, and checks slot availability against existing reservations with capacity constraints.
- **SecurityService** (`security_service.py`) — Structured audit logging for all auth events.
- **EmailService** (`email_service.py`) — SMTP delivery with retry and STARTTLS support.

### Models

SQLAlchemy models with a price matrix architecture: `ReglaPrecio` joins `CategoriaServicio` × `TipoVehiculo` × `TipoLavado` × `SubTipoLavado` × `TipoDetallado` to determine pricing and duration for any service combination.

## Features

### Booking Wizard

Multi-step reservation flow: vehicle type → service category → wash/detail type → date & time → customer details → confirmation. Supports multi-day bookings (Integral), time factors (dirt level, pet hair, etc.), and additional services.

### Pricing Engine

Matrix-based pricing with fixed prices (Normal wash) and estimated prices (Alta/Extrema requiring visual inspection). Prices are cached with versioned keys; editing any rule auto-invalidates the cache.

### Admin Panel

Full CRUD for all entities with a real-time dashboard showing today's reservations by status, active jobs, remaining capacity, and staff overview.

### Security

- Account lockout after failed attempts (15 min auto-reset)
- Session version invalidation (password change forces re-login)
- CSP, HSTS, X-Frame-Options, Referrer-Policy security headers
- Rate limiting on login (`10/min`), password reset (`5/min`), and reservation creation (`15/min`)
- Structured audit logging for all auth events

### Caching

Flask-Caching with Redis (production) or SimpleCache (development). View-level caching on catalog endpoints with versioned cache keys for selective invalidation.

### Rate Limiting

Flask-Limiter with configurable storage backend (Redis or in-memory). Global default: 200 req/min, 30 req/sec.

## API Endpoints (Public)

Base path: `/api/publica`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/tipos-vehiculo` | No | List active vehicle types |
| GET | `/categorias-servicio` | No | List active service categories |
| GET | `/tipos-lavado` | No | List wash types (normal, alta, extrema) |
| GET | `/subtipos-lavado` | No | List wash subtypes; filter by `?tipo_lavado_id=` or `?tipo_lavado_slug=` |
| GET | `/tipos-detallado` | No | List detailing types |
| GET | `/precio` | No | Price lookup — required: `vehiculo_slug`, `categoria_slug`; optional: `tipo_lavado_slug`, `subtipo_slug`, `tipo_detallado_slug` |
| GET | `/disponibilidad-multidia` | No | Multi-day slot check for Integral bookings — required: `fecha`; optional: `dias`, `duracion_min` |

Additional internal endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/horarios-disponibles?fecha=&duracion_min=` | Slot availability for a given date |
| GET | `/factores-tiempo-json?tipo=` | Time factors grouped by type |
| GET | `/servicios-json` | Legacy services list |

## Admin Panel

Accessible at `/admin/dashboard` after login. Sections:

| Section | Route | Functionality |
|---|---|---|
| Dashboard | `/admin/dashboard` | Today's stats, active jobs, capacity gauge |
| Reservas | `/admin/reservas` | List, search, detail, status workflow, print |
| Servicios | `/admin/servicios` | Service catalog, pricing rules, categories |
| Horarios | `/admin/horarios` | Weekly schedule configuration |
| Galería | `/admin/galeria` | Gallery images & categories |
| Clientes | `/admin/clientes` | Customer list & search |
| Factores | `/admin/factores-tiempo` | Time factor configuration |
| Usuarios | `/admin/usuarios` | Staff user management |

## Docker Deployment

```bash
# Build and start all services (app + MySQL + Redis)
docker-compose up -d --build

# Run the seeder
docker-compose exec app python seed.py

# Stop
docker-compose down
```

The Dockerfile uses `gunicorn` with 4 workers on port 5000. MySQL runs on host port 3307 (to avoid conflicts with local MySQL). Redis is optional — comment out the service and `depends_on` entry if you don't need cross-worker cache sharing.

## Testing

```bash
pip install pytest
pytest
```

## Default Credentials

| Email | Password | Role |
|---|---|---|
| admin@exclusiveautodetail.com | Admin1234! | admin |

## License

MIT
