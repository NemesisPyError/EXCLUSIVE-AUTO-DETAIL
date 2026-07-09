# AGENTS.md — Exclusive Auto Detail

## Quick Commands

```bash
# Dev setup
cp .env.example .env && pip install -r requirements.txt
createdb exclusive_autodetail
flask db upgrade
python seed.py          # skips if data exists; creates admin: admin@exclusiveautodetail.com / Admin1234!
flask run

# Testing
pytest                             # uses DB: exclusive_autodetail_test
pytest -x tests/test_reservas.py   # single file

# Docker
docker-compose up -d
docker-compose exec app flask db upgrade
docker-compose exec app python seed.py

# Migrations
flask db migrate -m "desc"
flask db upgrade
flask db downgrade

# Gunicorn production
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 "app:create_app()"
```

## Architecture

- **App factory**: `app.py::create_app(config_name=FLASK_ENV)`. Config classes in `config.py` selected by `FLASK_ENV` (`development`|`testing`|`production`).
- **Blueprints**: `main`, `auth`, `admin` (`/admin`), `reservas` (`/reservas`), `api` (`/api`), `api_publica` (`/api/publica`), `webhooks` (`/webhooks`).
- **Extensions** in `extensions.py`: `db`, `migrate`, `login_manager`, `csrf`, `limiter`, `cache`. All init'd in `create_app()`.
- **No CLI commands except flask-migrate**: entry points are `flask run`, `pytest`, `python seed.py`.

## Key Rules

- **Never modify backend models/routes/services unless explicitly asked.** The user's documented constraint is: only HTML, CSS, JavaScript, UX changes allowed.
- **Sprink `<form>` action handled by AJAX**: `POST /reservas/crear` receives JSON (not form-encoded). It's CSRF-exempt. `POST /login` expects form data.
- **Cache busting**: pricing cache via `pricing:epoch` in Redis, catalog cache via `catalog:epoch`. Call `invalidar_cache_prefijo()` after changing seed data.
- **Soft delete**: `Reserva.deleted_at` column, queries filter `deleted_at.is_(None)`.
- **Auth**: protect admin routes with `@role_required('admin', 'empleado')` from `decorators.py`.
- **Test DB**: separate database `exclusive_autodetail_test`. Tests create/drop all tables per session. Rate limiter is globally disabled via monkeypatch in `conftest.py`.
- **Seed is idempotent**: checks `Servicio.query.count() > 0` and exits if data exists.

## Frontend Wizard (Critical Convention)

- **12 JS files** in `static/js/wizard-*.js`, loaded at the bottom of `templates/reservas/nueva.html`.
- **Global state**: `window.WizardState` (singleton in `wizard-state.js`). All modules read/write it. State lives in `WizardState.selections`.
- **Script load order in nueva.html matters**: `wizard-vehiculo-autocomplete.js` must load **before** `wizard-main.js`. If autocomplete loads after, `WizardMain.init()` captures `undefined` for the autocomplete reference and the brand autocomplete never registers its `input` listener.
- **CSS**: Wizard styles are 100% in `static/css/wizard.css` (~2600 lines). Bootstrap 5 is the global framework.
- **5 wizard steps**: Servicio → Vehiculo → Agenda → Datos → Confirmar. Pane IDs: `paso-1` through `paso-5`.
- **Step transitions**: CSS opacity+translateY fade (120ms) in `wizard-navigation.js::goStep()`.
- **Autocomplete dropdown**: uses class `.ead-autocomplete-wrapper` (position:relative) + `.ead-autocomplete-dropdown` (position:absolute, z-index:1100). JS creates `.ead-autocomplete-item` children inside the dropdown.
- **Price display**: `WizardPricing.fetchPrecio()` triggers when all 4 params known (servicio + tipo + segmento + suciedad). Results cached in `WizardState.preciosCache`. Pricing engine backend uses `PrecioServicio` table.

## Reservation Creation (The Only Way)

- **Single endpoint**: `POST /reservas/crear` → `ReservationBuilder.build_reservation(data)`.
- **No admin creation, no batch import, no webhooks.**
- Builder does in order: validate input → get/create cliente → get/create vehiculo → lookup service/suciedad/estado → calculate duracion → validate within hours → price service + adicionales → assign box atomically (`SELECT ... FOR UPDATE`) → create Reserva + ReservaAdicional + optional SolicitudCatalogo → commit.
- **Box assignment**: iterates compatible boxes, locks rows with `FOR UPDATE`, checks time overlap. Returns HTTP 409 if no box available.
