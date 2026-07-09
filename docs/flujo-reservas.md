# Flujo de Reservas — Documentación Técnica

> **Proyecto:** Exclusive Auto Detail  
> **Propósito:** Documentar el flujo completo de creación de una reserva, desde la UI del wizard hasta el commit en base de datos.

---

## Índice

1. [Arquitectura General](#1-arquitectura-general)
2. [Rutas y Endpoints](#2-rutas-y-endpoints)
3. [Modelo de Datos: Reserva](#3-modelo-de-datos-reserva)
4. [Wizard Cliente (Frontend)](#4-wizard-cliente-frontend)
5. [API Pública (Backend)](#5-api-pública-backend)
6. [ReservationBuilder (Lógica de Negocio)](#6-reservationbuilder-lógica-de-negocio)
7. [Pricing Engine](#7-pricing-engine)
8. [Planificador de Ocupación (Disponibilidad)](#8-planificador-de-ocupación-disponibilidad)
9. [Máquina de Estados](#9-máquina-de-estados)
10. [Validaciones](#10-validaciones)
11. [Diagrama de Secuencia](#11-diagrama-de-secuencia)
12. [Flujo Admin (Solo Lectura/Edición)](#12-flujo-admin-solo-lecturaedición)

---

## 1. Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     Navegador (Cliente)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Wizard SPA (nueva.html)                 │   │
│  │  ┌──────┐ ┌──────────┐ ┌───────┐ ┌─────┐ ┌───────┐ │   │
│  │  │ Paso │ │ Paso 2   │ │ Paso  │ │ Paso│ │ Paso  │ │   │
│  │  │ 1    │ │ Vehículo │ │ 3     │ │ 4   │ │ 5     │ │   │
│  │  │ Svc  │ │          │ │ Agenda│ │Datos│ │Confir.│ │   │
│  │  └──────┘ └──────────┘ └───────┘ └─────┘ └───────┘ │   │
│  │                                                    │   │
│  │  12 × wizard-*.js (vanilla JS, sin framework)       │   │
│  │  Estado global: WizardState.selections              │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │ fetch(AJAX)                        │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                Flask (Python 3.x)                           │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────┐            │
│  │              Routers                         │            │
│  │  /reservas/nueva (GET — render template)    │            │
│  │  /reservas/crear (POST — crear reserva)     │            │
│  │  /api/publica/*    (GET — datos referenciales)│           │
│  └──────────────────────┬──────────────────────┘            │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────┐            │
│  │         Services                             │            │
│  │  ReservationBuilder → orquesta la creación   │            │
│  │  PricingEngine      → precio caching         │            │
│  │  PlanificadorOcupac → slots + asignar box    │            │
│  │  CalculadorDuracion → duración dinámica      │            │
│  │  EstadoMachine      → transiciones           │            │
│  │  Validaciones       → formato, fecha, hora   │            │
│  └──────────────────────┬──────────────────────┘            │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────┐            │
│  │         PostgreSQL                           │            │
│  │  reservas, clientes, vehiculos, servicios,  │            │
│  │  precios_servicio, boxes, horarios, etc.    │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Rutas y Endpoints

### 2.1 Frontend

| Método | Ruta | Blueprint | Función | Propósito |
|--------|------|-----------|---------|-----------|
| GET | `/reservas/nueva` | `reservas_bp` | `nueva()` | Renderiza wizard (nueva.html) |
| POST | `/reservas/crear` | `reservas_bp` | `crear()` | Crea reserva (JSON) |
| GET | `/reservas/confirmacion/<token>` | `reservas_bp` | `confirmacion()` | Página post-creación |

**POST /reservas/crear**  
- Rate limit: 15 req/min (por IP)
- CSRF exempt (llamado vía AJAX)
- Request: `Content-Type: application/json`
- Response 201: `{ success, reserva_id, confirmacion_token }`
- Response 400: `{ success: false, errors: {...} }`
- Response 500: `{ success: false, error: "..." }`

### 2.2 API Pública (solo GET)

| Ruta | Cache | Propósito |
|------|-------|-----------|
| `/api/publica/tipos-vehiculo` | 86400s | Tipos de vehículo |
| `/api/publica/categorias-servicio` | 86400s | Categorías de servicio |
| `/api/publica/segmentos` | 86400s | Segmentos (tamaños) |
| `/api/publica/niveles-suciedad` | 86400s | Niveles de suciedad |
| `/api/publica/servicios?tipo=` | 3600s | Servicios filtrados por tipo |
| `/api/publica/precio` | 600s | Precio por combo (rate limit: 30/min) |
| `/api/publica/disponibilidad` | — | Slots disponibles |
| `/api/publica/marcas/buscar?q=` | 3600s | Autocomplete marcas |
| `/api/publica/modelos/buscar?q=&marca_id=` | 3600s | Autocomplete modelos |
| `/api/publica/modelos/detectar-marca?q=` | 3600s | Infiere marca desde modelo |

---

## 3. Modelo de Datos: Reserva

**Archivo:** `models/reserva.py` · **Tabla:** `reservas`

### Columnas

| Columna | Tipo | Nulable | Descripción |
|---------|------|---------|-------------|
| `id` | `int PK` | No | ID autoincremental |
| `cliente_id` | `FK → clientes.id` | No | Cliente asociado |
| `vehiculo_id` | `FK → vehiculos.id` | No | Vehículo asociado |
| `servicio_id` | `FK → servicios.id` | No | Servicio base |
| `estado_reserva_id` | `FK → estados_reserva.id` | No | Estado actual |
| `nivel_suciedad_id` | `FK → niveles_suciedad.id` | No | Nivel de suciedad |
| `box_id` | `FK → boxes.id` | Sí | Box asignado |
| `usuario_asignado_id` | `FK → usuarios.id` | Sí | Empleado asignado |
| `fecha` | `date` | No | Fecha del servicio |
| `hora_inicio` | `time` | No | Hora programada |
| `duracion_total_min` | `smallint` | No | CK > 0 |
| `fecha_entrega_estimada` | `date` | Sí | Para servicios multi-día |
| `hora_entrega_estimada` | `time` | Sí | Estimación de entrega |
| `precio_estimado_base` | `int` | No | Precio base estimado |
| `precio_estimado_adicionales` | `int` | No | Suma adicionales |
| `precio_final_base` | `int` | Sí | Precio real (post-facturación) |
| `precio_final_adicionales` | `int` | Sí | Adicionales reales |
| `motivo_ajuste_precio` | `text` | Sí | Razón de ajuste |
| `confirmacion_token` | `varchar(64)` | Sí | Token único post-creación |
| `observaciones_cliente` | `text` | Sí | Notas del cliente |
| `observaciones_internas` | `text` | Sí | Notas internas |
| `reagendado_de` | `FK → reservas.id` | Sí | Reserva original (si se reagendó) |
| `created_at` | `timestamptz` | No | Fecha de creación |
| `updated_at` | `timestamptz` | No | Fecha de última modificación |
| `created_by` | `FK → usuarios.id` | Sí | Quién creó |
| `updated_by` | `FK → usuarios.id` | Sí | Quién modificó |
| `deleted_at` | `timestamptz` | Sí | Soft delete |

### Constraints

- `ck_duracion_positiva`: `duracion_total_min > 0`
- `ix_reservas_box_fecha_hora`: Índice compuesto sobre `(box_id, fecha, hora_inicio)` para búsquedas de disponibilidad.

### Relaciones

```
Reserva ──belongs_to──> Cliente
Reserva ──belongs_to──> Vehiculo
Reserva ──belongs_to──> Servicio
Reserva ──belongs_to──> EstadoReserva
Reserva ──belongs_to──> NivelSuciedad
Reserva ──belongs_to──> Box
Reserva ──belongs_to──> Usuario (asignado)
Reserva ──has_many───> ReservaAdicional
Reserva ──has_many───> EstadoCambio
Reserva ──has_many───> FotografiaReserva
```

---

## 4. Wizard Cliente (Frontend)

**Template:** `templates/reservas/nueva.html`  
**Scripts:** 12 archivos en `static/js/wizard-*.js`, vanilla JavaScript sin framework.

### 4.1 Módulos JS

| Archivo | Objeto global | Responsabilidad |
|---------|--------------|-----------------|
| `wizard-state.js` | `WizardState` | Estado compartido (selecciones, caches) |
| `wizard-helpers.js` | `WizardHelpers` | Formateo (Guaraníes, duración, escape HTML) |
| `wizard-api.js` | `WizardAPI` | Wrapper fetch hacia `/api/publica/*` y `/reservas/crear` |
| `wizard-validations.js` | `WizardValidations` | Validación de cada paso antes de navegar |
| `wizard-pricing.js` | `WizardPricing` | Consulta de precios con cache y abort controller |
| `wizard-rendering.js` | `WizardRendering` | Renderiza cards, chips, detalle inline, acordeones |
| `wizard-summary.js` | `WizardSummary` | Renderiza resumen lateral (sidebar) + paso 5 |
| `wizard-availability.js` | `WizardAvailability` | Carga slots, date chips, mejor slot banner |
| `wizard-navigation.js` | `WizardNavigation` | Transición entre pasos, barra de progreso |
| `wizard-vehiculo-autocomplete.js` | `WizardVehiculoAutocomplete` | Autocomplete marca/modelo |
| `wizard-main.js` | `WizardMain` | Entry point: inicializa, bindea botones, construye payload, submit |
| `wizard-estado.js` | — (en desuso?) | Módulo de transiciones (no usado en wizard) |

### 4.2 Estado Global (`WizardState`)

```javascript
{
  currentStep: 1,          // Paso actual (1-5)
  totalSteps: 5,           // Total pasos
  maxStepReached: 1,       // Máximo paso alcanzado
  tiposVehiculo: [...],    // Cache de tipos
  segmentos: [...],        // Cache segmentos
  servicios: { base: [], adicional: [], paquete: [] }, // Cache servicios
  nivelesSuciedad: [...],  // Cache niveles
  preciosCache: {},        // Cache de precios
  selections: {            // Selecciones del usuario
    tipo_vehiculo_id: null,
    segmento_id: null,
    servicio_id: null,
    nivel_suciedad_id: null,
    adicionales_ids: [],
    fecha: null,
    hora_inicio: null,
    nombre: '', apellido: '', telefono: '', cedula: '', email: '',
    marca: '', modelo: '', marca_id: null, modelo_id: null,
    anio: null, color: '', chapa: '', combustible: '', transmision: '',
    vehiculo_id: null,
  },
  precio: null,            // Precio actual
  duracion: 60,            // Duración en minutos
  fechaEntrega: null,
  submitting: false,       // Flag anti-doble-click
}
```

### 4.3 Pasos del Wizard

| Paso | ID Pane | URL State | Contenido | Validación |
|------|---------|-----------|-----------|------------|
| 1 Servicio | `paso-1` | `#paso=1` | Acordeón categorías → service cards premium → panel detalle inline (suciedad pills + adicionales chips + precio badge) | servicio_id seleccionado + nivel_suciedad_id |
| 2 Vehículo | `paso-2` | `#paso=2` | Autocomplete marca/modelo → tipo/segmento cards → opcionales (año, color, etc.) | tipo_vehiculo_id + segmento_id |
| 3 Agenda | `paso-3` | `#paso=3` | Date chips (Hoy/Mañana/Elegir) → slot chips → "Mejor slot" banner | fecha + hora_inicio |
| 4 Datos | `paso-4` | `#paso=4` | Formulario nombre, apellido, teléfono, email, cédula | nombre, apellido, teléfono (formato PY) |
| 5 Confirmar | `paso-5` | `#paso=5` | Resumen completo, toggle desglose precio, botón "Confirmar Reserva" | — (confirmación final) |

### 4.4 Inicialización (wizard-main.js)

```
DOMContentLoaded
  └─ WizardMain.init()
       ├─ fetchServicios('base')      → ns.servicios.base
       ├─ fetchServicios('adicional') → ns.servicios.adicional
       ├─ fetchServicios('paquete')   → ns.servicios.paquete + renderPaquetes()
       ├─ fetchNivelesSuciedad()      → ns.nivelesSuciedad
       ├─ fetchTiposVehiculo()        → ns.tiposVehiculo
       ├─ fetchSegmentos()            → ns.segmentos
       ├─ renderServiciosBase()
       ├─ bindButtons()               → next/prev navegación
       ├─ bindDatePicker()            → fecha mínima = hoy
       └─ WizardVehiculoAutocomplete.init()  → input listeners
```

### 4.5 Navegación (wizard-navigation.js)

```
nextStep()
  └─ validateStep(currentStep) → si falla, muestra error, no avanza
  └─ collectFormData()         → Lee inputs del DOM → WizardState.selections
  └─ goStep(currentStep + 1)

prevStep()
  └─ collectFormData()
  └─ goStep(currentStep - 1)

goStep(n)
  └─ Fade transition (120ms opacity + translateY)
  └─ Actualiza indicadores, progress bar, aria
  └─ Inicializa paso:
       n=1: renderServiciosBase, renderPaquetes, restore detalle
       n=2: renderTiposVehiculo, renderSegmentos, restore selección
       n=3: loadSlotsForToday(), set fecha default
       n=5: renderStep5Summary()
  └─ renderResumen() (sidebar)
```

### 4.6 Envío (buildPayload + submit)

```
WizardMain.submit()
  └─ ns.submitting = true (deshabilita botón)
  └─ collectFormData()
  └─ buildPayload():
       {
         tipo_vehiculo_id, segmento_id, servicio_id,
         nivel_suciedad_id, adicionales_ids,
         fecha, hora_inicio,
         nombre, apellido, telefono, cedula, email,
         marca, modelo, marca_id, modelo_id,
         anio, color, chapa, combustible, transmision,
         vehiculo_id,
       }
  └─ API.submitReserva(payload) → fetch POST /reservas/crear
       ├─ éxito → window.location = /reservas/confirmacion/<token>
       └─ error → showBanner(mensaje), re-habilita botón
```

---

## 5. API Pública (Backend)

**Archivo:** `routes/api_routes.py` · **Blueprint:** `api_publica_bp`

### 5.1 Endpoints de consulta

Todos retornan `{ success: true, ... }` o `{ success: false, error: "..." }`.

#### `GET /api/publica/servicios`

```
Query params:
  tipo:      'base' | 'adicional' | 'paquete' (filtra por Servicio.tipo)
  categoria_slug: slug de CategoriaServicio

Response:
  { success: true, servicios: [
    { id, nombre, slug, descripcion, tipo, categoria_id,
      categoria_nombre, requiere_inspeccion_previa,
      requiere_varios_dias, dias_bloqueo, activo,
      composicion: [{ servicio_id, nombre, es_principal, orden }]  // solo si tipo='paquete'
    }
  ]}
```

Cache: 3600s con key por query string.

#### `GET /api/publica/precio`

```
Params: servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id
Rate limit: 30 req/min

Response:
  { success: true, precio: { precio: int, duracion_minutos: int } }
  └─ 404 si no hay precio configurado
```

Cache: 600s en Redis (con invalidación por `pricing:epoch`).

#### `GET /api/publica/disponibilidad`

```
Params: fecha (YYYY-MM-DD), tipo_vehiculo_id, duracion_min (default 60)

Response:
  { success: true, fecha, duracion_min, slots: [
    { hora: "08:00", disponible: bool },
    { hora: "08:30", disponible: bool },
    ...
  ]}
```

Sin cache (en tiempo real). Usa `PlanificadorOcupacion.slots_disponibles()`.

#### `GET /api/publica/marcas/buscar`

```
Params: q (mín 1 char)

Response:
  { success: true, marcas: [{ id, nombre, slug, pais_origen, logo }] }

Cache: 3600s. SQL: LIKE %q%, LIMIT 12, solo activas.
```

#### `GET /api/publica/modelos/buscar`

```
Params: q, marca_id (opcional), marca_slug (opcional)

Response:
  { success: true, modelos: [{
    id, marca_id, marca_nombre, nombre, slug,
    tipo_vehiculo_id, tipo_vehiculo_nombre,
    segmento_id, segmento_nombre,
    anio_desde, anio_hasta
  }]}

Cache: 3600s. LIMIT 20. Joineado con marca, tipo, segmento.
```

---

## 6. ReservationBuilder (Lógica de Negocio)

**Archivo:** `services/reservation_builder.py` · **Clase:** `ReservationBuilder`

Es el **único lugar en producción** donde se instancia `Reserva()`. Método principal:

```python
ReservationBuilder.build_reservation(data: dict) -> Reserva
```

### Flujo interno

```
build_reservation(data)
│
├─ 1. _validate_input(data)
│    ├─ servicio_id         → requerido
│    ├─ nivel_suciedad_id   → requerido
│    ├─ fecha               → requerido + validar_fecha_futura()
│    ├─ hora_inicio         → requerido
│    ├─ nombre + apellido   → requeridos
│    └─ telefono            → validar_telefono_py() si presente
│    └→ Si errores → raise ReservationValidationError(errors)
│
├─ 2. _get_or_create_cliente(data)
│    ├─ Busca Cliente por teléfono
│    ├─ Si no existe: crea (nombre, apellido, telefono, cedula, email)
│    ├─ Si teléfono vacío: genera "sin-telefono-{timestamp}" (fallback)
│    └─ Maneja IntegrityError (race condition)
│    └→ Retorna Cliente
│
├─ 3. _get_or_create_vehiculo(data, cliente)
│    ├─ Si vehiculo_id: busca existente y verifica cliente_id
│    ├─ Si modelo_id: busca ModeloVehiculo → obtiene marca_id, tipo, segmento
│    ├─ Si no: usa marca_texto/modelo_texto, busca Marca por nombre
│    └─ Crea Vehiculo(cliente_id, marca_id, modelo_id, marca_texto,
│         modelo_texto, tipo_vehiculo_id, segmento_id, anio, color,
│         chapa, combustible, transmision)
│    └→ Retorna Vehiculo
│
├─ 4. db.session.get(Servicio, data.servicio_id)
│    └→ Si no existe → error
│
├─ 5. db.session.get(NivelSuciedad, data.nivel_suciedad_id)
│    └→ Si no existe → error
│
├─ 6. EstadoReserva.query.filter_by(nombre='Pendiente').first()
│    └→ Si no existe → error
│
├─ 7. CalculadorDuracion.calcular_duracion(
│       servicio_id, tipo_vehiculo_id, segmento_id,
│       nivel_suciedad_id, adicionales_ids)
│    └→ Suma duración base + adicionales + margen 15 min
│    └→ Retorna minutos totales
│
├─ 8. validar_dentro_horario(dia_semana, hora_inicio, duracion)
│    ├─ Obtiene horario del día (PlanificadorOcupacion.horario_activo)
│    ├─ Verifica hora_inicio >= horario.hora_inicio
│    └─ Verifica hora_inicio + duracion <= horario.hora_fin
│    └→ Si falla → error
│
├─ 9. PricingEngine.obtener_precio(
│       servicio_id, tipo_vehiculo_id, segmento_id, nivel_suciedad_id)
│    └→ Busca PrecioServicio (con cache)
│    └→ Si no existe → error
│    └→ precio_base = resultado.precio
│
├─ 10. Para cada adicional_id:
│      PricingEngine.obtener_precio(...) → suma precio_adicionales
│
├─ 11. _asignar_box_atomico(tipo_vehiculo_id, fecha, hora_inicio, duracion)
│      ├─ Obtiene boxes compatibles (BoxTipoVehiculo)
│      ├─ Para cada box:
│      │   SELECT FOR UPDATE reservas WHERE box_id=fecha
│      │   → verifica overlap de horarios
│      ├─ Primer box sin overlap → retorna box.id
│      └─ Si ninguno disponible → error
│
├─ 12. Si servicio.requiere_varios_dias:
│       fecha_entrega = fecha + (dias_bloqueo - 1)
│
├─ 13. Crea Reserva(
│        cliente_id, vehiculo_id, servicio_id,
│        estado_reserva_id='Pendiente',
│        nivel_suciedad_id, box_id,
│        fecha, hora_inicio, duracion_total_min,
│        fecha_entrega_estimada,
│        precio_estimado_base, precio_estimado_adicionales)
│      db.session.add(reserva)
│      db.session.flush() → obtiene reserva.id
│
├─ 14. Para cada adicional_id:
│       Crea ReservaAdicional(reserva_id, servicio_id,
│                             precio_aplicado, tiempo_aplicado_min)
│
├─ 15. Si vehículo NO catalogado (modelo_id is None):
│       Crea SolicitudCatalogo(marca_texto, modelo_texto,
│                               tipo, segmento, cliente, vehiculo)
│
├─ 16. db.session.commit()
│      └→ Retorna reserva
│
└─ Excepciones:
     ├─ ReservationValidationError → rollback + raise
     └─ Exception → rollback + raise
```

### Asignación Atómica de Box

```python
_asignar_box_atomico(tipo_vehiculo_id, fecha, hora_inicio, duracion_min)
  → boxes = PlanificadorOcupacion.boxes_disponibles(tipo_vehiculo_id)
  → Por cada box:
      reservas = Reserva.query.filter(
          box_id=box.id, fecha=fecha, deleted_at=None
      ).with_for_update().all()
      → Si no hay overlap horario → retorna box.id
  → Si ninguno → retorna None
```

Usa `SELECT ... FOR UPDATE` para evitar race conditions en booking concurrente.

---

## 7. Pricing Engine

**Archivo:** `services/pricing_service.py` · **Clase:** `PricingEngine`

### Modelo: `PrecioServicio`

Almacena precio y duración para cada combinación de:
- `servicio_id`
- `tipo_vehiculo_id`
- `segmento_id`
- `nivel_suciedad_id`

### Cache

```
Clave: "pricing:v{version}/{servicio_id}/{tipo_vehiculo_id}/{segmento_id}/{nivel_suciedad_id}"
TTL: 600s (10 minutos)
Invalidación: incrementar "pricing:epoch" → invalida todo
```

### Métodos

| Método | Descripción |
|--------|-------------|
| `obtener_precio(svc_id, tipo_id, seg_id, suciedad_id)` | Precio individual + duración |
| `obtener_precios_servicio(svc_id)` | Todos los precios de un servicio (sin cache por combo) |
| `invalidar_cache_precio()` | Incrementa epoch → invalida todo |

---

## 8. Planificador de Ocupación (Disponibilidad)

**Archivo:** `services/duracion.py`

### CalculadorDuracion

```
calcular_duracion(servicio_id, tipo_vehiculo_id, segmento_id,
                  nivel_suciedad_id, adicionales_ids=None)
  → Busca PrecioServicio para servicio base → minutos base
  → Suma duración de cada adicional
  → + MARGEN_TALLER_MINUTOS = 15
  → Retorna total minutos
```

### PlanificadorOcupacion

| Método | Descripción |
|--------|-------------|
| `boxes_disponibles(tipo_vehiculo_id)` | Boxes compatibles vía BoxTipoVehiculo |
| `hay_disponibilidad(box_id, fecha, hora, duracion)` | Verifica si un slot está libre en un box específico |
| `asignar_box(tipo_id, fecha, hora, duracion)` | Busca primer box libre (sin FOR UPDATE, para consulta) |
| `horario_activo(dia_semana)` | Horario laboral del día |
| `slots_disponibles(fecha, duracion, tipo_id)` | Genera slots de 30 min, marca disponibles |
| `validar_multidia(fecha, dias, duracion)` | Para servicios multi-día |
| `obtener_agenda_dia(fecha)` | Vista completa para admin (boxes + reservas) |

### Generación de Slots

```
slots_disponibles(fecha, duracion_min, tipo_vehiculo_id)
  ├─ horario = horario_activo(fecha.isoweekday())
  ├─ boxes = boxes_disponibles(tipo_vehiculo_id)
  ├─ Para cada hora desde horario.hora_inicio hasta horario.hora_fin
  │   con intervalo de 30 min:
  │   ├─ Para cada box: verifica overlap con reservas existentes
  │   └─ Si al menos un box libre → slot.disponible = true
  └─ Retorna [{ hora: "HH:MM", disponible: bool }, ...]
```

---

## 9. Máquina de Estados

**Archivo:** `services/estado_machine.py` · **Clase:** `EstadoMachine`

### Transiciones

```
Pendiente ──→ Confirmada ──→ Recibida ──→ En Proceso ──→ Lista ──→ Entregada
    │             │             │              │
    └──→ Cancelada ←───────────┴──────────────┘
```

| Estado Actual | Puede pasar a |
|---------------|--------------|
| Pendiente | Confirmada, Cancelada |
| Confirmada | Recibida, Cancelada |
| Recibida | En Proceso, Cancelada |
| En Proceso | Lista, Cancelada |
| Lista | Entregada |
| Entregada | _(terminal)_ |
| Cancelada | _(terminal)_ |

### Métodos

```python
EstadoMachine.validar_transicion(estado_actual_id, estado_nuevo_id)
  → (True, '') si la transición es válida
  → (False, 'mensaje de error') si no
```

---

## 10. Validaciones

**Archivo:** `services/validaciones.py`

| Función | Inputs | Regla |
|---------|--------|-------|
| `validar_email(email)` | string | Regex email estándar. Vacío = OK |
| `validar_telefono_py(tel)` | string | `0991XXXXXX` o `+595991XXXXXX` (10 dígitos después del código) |
| `validar_fecha_futura(fecha)` | date | `fecha >= date.today()` |
| `validar_dentro_horario(dia, hora, duracion)` | int, time, int | Hora dentro del horario laboral del día |
| `validar_disponibilidad(tipo_id, fecha, hora, duracion)` | int, date, time, int | Existe al menos un box libre |

---

## 11. Diagrama de Secuencia

```
Usuario              Wizard JS           API Pública          ReservationBuilder     DB
   │                     │                    │                    │                 │
   │── GET /reservas/nueva─────────────────────│────────────────────│─────────────────│─→
   │←── nueva.html + 12 × wizard-*.js ────────│────────────────────│─────────────────│──
   │                     │                     │                    │                 │
   │                     │── fetchServicios(base/adicional/paquete)─│─────────────────│─→
   │                     │── fetchNivelesSuciedad() ────────────────│─────────────────│─→
   │                     │── fetchTiposVehiculo() ──────────────────│─────────────────│─→
   │                     │── fetchSegmentos() ──────────────────────│─────────────────│─→
   │←── (renderiza cards, chips, acordeones) ──│────────────────────│─────────────────│──
   │                     │                     │                    │                 │
   │──(selecciona servicio, suciedad)──────────│────────────────────│─────────────────│─→
   │                     │── GET /precio?servicio_id=... ───────────│─────────────────│─→
   │←── { precio, duracion_minutos } ──────────│────────────────────│─────────────────│──
   │                     │                     │                    │                 │
   │──(escribe "toyo" en marca)────────────────│────────────────────│─────────────────│─→
   │                     │── GET /marcas/buscar?q=toyo ─────────────│─────────────────│─→
   │←── ["Toyota", ...] ───────────────────────│────────────────────│─────────────────│──
   │                     │                     │                    │                 │
   │──(selecciona fecha)───────────────────────│────────────────────│─────────────────│─→
   │                     │── GET /disponibilidad?fecha=... ─────────│─────────────────│─→
   │                     │                     │── slots_disponibles() ───────────────│─→
   │←── { slots: [...] } ─────────────────────│────────────────────│─────────────────│──
   │                     │                     │                    │                 │
   │──(completa datos personales)──────────────│────────────────────│─────────────────│─→
   │──(hace clic "Confirmar Reserva")──────────│────────────────────│─────────────────│─→
   │                     │── POST /reservas/crear ──────────────────│─────────────────│─→
   │                     │                     │                    │── _validate_input
   │                     │                     │                    │── _get_or_create_cliente
   │                     │                     │                    │── _get_or_create_vehiculo
   │                     │                     │                    │── calcular_duracion
   │                     │                     │                    │── validar_dentro_horario
   │                     │                     │                    │── obtener_precio
   │                     │                     │                    │── _asignar_box_atomico
   │                     │                     │                    │── (SELECT ... FOR UPDATE)
   │                     │                     │                    │── (INSERT reservas)
   │                     │                     │                    │── (INSERT adicionales)
   │                     │                     │                    │── (INSERT solicitud_catalogo)
   │                     │                     │                    │── COMMIT
   │←── { success, reserva_id, confirmacion_token } ───────────────│─────────────────│──
   │                     │                     │                    │                 │
   │── (redirect) ───────│─────────────────────│────────────────────│─────────────────│─→
   │── GET /reservas/confirmacion/<token> ─────│────────────────────│─────────────────│─→
```

---

## 12. Flujo Admin (Solo Lectura/Edición)

**Blueprint:** `admin_reservas_bp` en `routes/admin/reservas.py`

El admin **no puede crear reservas**. Solo opera sobre existentes.

| Ruta | Método | Función | Propósito |
|------|--------|---------|-----------|
| `/admin/reservas` | GET | `listar_reservas()` | Lista + filtros (fecha, estado, búsqueda) |
| `/admin/reservas/<id>` | GET | `detalle_reserva()` | Detalle completo + timeline |
| `/admin/reservas/<id>/editar` | GET/POST | `editar_reserva()` | Edita cliente + vehículo + observaciones |
| `/admin/reservas/<id>/estado` | POST | `cambiar_estado()` | Cambia estado (usa EstadoMachine) |
| `/admin/reservas/<id>/asignar` | POST | `asignar_empleado()` | Asigna empleado al box |
| `/admin/reservas/<id>/eliminar` | POST | `eliminar_reserva()` | Soft delete |
| `/admin/reservas/eliminar-masivo` | POST | `eliminar_reservas_masivo()` | Bulk soft delete |

### Estados editables

En `editar_reserva.html`:
- `nombre`, `apellido`, `cedula`, `telefono`, `email` (del cliente)
- `marca`, `modelo`, `anio`, `color` (del vehículo)
- `observaciones` (de la reserva)

No se permite cambiar: servicio, fecha, hora, box, precio desde admin.

---

## Apéndice: Archivos Clave

| Área | Archivo | Propósito |
|------|---------|-----------|
| Template wizard | `templates/reservas/nueva.html` | UI del wizard 5 pasos |
| Template confirmación | `templates/reservas/confirmacion.html` | Página post-creación |
| Ruta reservas | `routes/reservas.py` | GET /nueva, POST /crear, GET /confirmacion |
| Ruta API | `routes/api_routes.py` | Endpoints públicos GET |
| Ruta admin | `routes/admin/reservas.py` | CRUD admin |
| Servicio builder | `services/reservation_builder.py` | Lógica de creación (único lugar) |
| Servicio pricing | `services/pricing_service.py` | Precios con cache |
| Servicio duración | `services/duracion.py` | Cálculo duración + planificador |
| Servicio validaciones | `services/validaciones.py` | Validaciones |
| Servicio estados | `services/estado_machine.py` | Máquina de estados |
| Servicio serializers | `services/serializers.py` | Serialización API |
| Modelo reserva | `models/reserva.py` | SQLAlchemy model |
| JS state | `static/js/wizard-state.js` | Estado global |
| JS api | `static/js/wizard-api.js` | Fetch wrappers |
| JS main | `static/js/wizard-main.js` | Entry point, submit |
| JS navigation | `static/js/wizard-navigation.js` | Transición pasos |
| JS rendering | `static/js/wizard-rendering.js` | Renderiza DOM |
| JS pricing | `static/js/wizard-pricing.js` | Precios cliente |
| JS availability | `static/js/wizard-availability.js` | Slots cliente |
| JS validation | `static/js/wizard-validations.js` | Validación cliente |
| JS summary | `static/js/wizard-summary.js` | Resumen sidebar |
| JS autocomplete | `static/js/wizard-vehiculo-autocomplete.js` | Autocomplete |
| CSS | `static/css/wizard.css` | Estilos wizard (~2600 líneas) |
| Tests | `tests/test_reservas.py` | Tests de creación |
