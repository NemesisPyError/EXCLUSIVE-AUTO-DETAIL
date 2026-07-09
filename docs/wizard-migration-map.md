# Wizard CSS Migration Map — `nueva.html` → `components.css`

> Generado en paso 3.1 del plan `continuacion-fases-3-4-6.md`.
> Revisar antes de comenzar la migración de cada paso (3.2–3.6).

## Direct Mappings (migrar sin cambios)

| Clase wizard | Equivalente | Dónde se usa |
|---|---|---|
| `svc-detail-content` | `ead-card` | Panel detalle de servicio (paso 1) |
| `alert-custom` | `ead-alert ead-alert-info` | Banner "Revisa los datos" (paso 5) |
| `btn-commit` | `btn-primary.btn-commit` | Botón "Confirmar Reserva" — ya existe en components.css |
| `btn-primary` | `btn-primary` | Botones "Reservar" en cards de servicio — ya correcto |
| `btn-secondary` (en wizard) | `btn-secondary` | Botones "Ver Servicios", "Atrás" — ya correcto |

## Clases wizard que NO se migran (se mantienen como están)

Estas son específicas del wizard y no tienen equivalente en components.css. Permanecen en wizard.css.

| Clase | Función |
|---|---|
| `wizard-container` | Layout raíz (max-width, padding, safe-area) |
| `wizard-layout` | Flex row steps + sidebar |
| `wizard-steps-area` | Columna principal de pasos |
| `wizard-sidebar` | Sticky sidebar desktop |
| `wizard-sidebar-title` | Título del sidebar |
| `progress-steps`, `step`, `circle`, `label` | Stepper desktop (5 pasos) |
| `step-indicator` | "PASO X DE 5" |
| `ead-step-indicator` | JS hook (click para navegar) |
| `ead-step-pane` | Pane transition (opacity/translateY) |
| `wizard-nav` | Footer de navegación (Atrás/Continuar) + sticky mobile |
| `option-grid` | Grid de cards (tipo vehículo, segmento) |
| `btn-expand-more` | Toggle "Más información" |
| `date-chips`, `date-chip`, `date-chip-picker` | Selector rápido de fecha |
| `ead-autocomplete-wrapper/dropdown/item` | Autocomplete de marca/modelo |
| `ead-loading` | Spinner de carga |
| `ead-field-error` | Mensaje de validación inline |
| `mobile-sticky-footer` | Footer fijo mobile |
| `msf-price`, `msf-amount`, `msf-resume-btn` | Elementos del footer mobile |
| `bs-overlay`, `bottom-sheet`, `bs-handle`, `bs-header`, `bs-title`, `bs-close`, `bs-body` | Bottom sheet resumen |
| `progress-mobile`, `progress-mobile-label`, `progress-mobile-bar`, `progress-mobile-fill` | Barra de progreso mobile |
| `text-muted-custom` | Color de texto secundario |

## Observaciones por paso

### Paso 1 (Servicio)
- Cards de paquete: usan `data-servicio-id`, no clase específica — no migrar
- Chips de adicionales: clase `chip` genérica, definida en wizard.css — no migrar
- Acordeón categorías: clases propias en wizard.css — no migrar
- `svc-detail-content` → `ead-card` ✅ migrar

### Paso 2 (Vehículo)
- Autocomplete clases: mantener
- Banner "encontrado en el catálogo": verde con clase propia → migrar a variante success de alert/badge
- Grid tipo/tamaño: `option-grid` con `ead-select-card` dentro — las cards internas pueden migrar a `.ead-select-card`

### Paso 3 (Fecha y Hora)
- `date-chips` / `date-chip`: son tabs de tipo segmented-control. No hay equivalente. Mantener.
- Grid de horarios: slots creados por JS, clases propias. Mantener.

### Paso 4 (Datos personales)
- Inputs sin clase específica: los `<input>` ya se beneficiarán de `ead-input` si se la agregamos
- `ead-field-error`: mantener (o migrar a `note-danger` si se crea)

### Paso 5 (Confirmación)
- `alert-custom` → `ead-alert ead-alert-info` ✅ migrar
- Resumen: no tiene clases específicas, usa estructura HTML directa
- `btn-primary.btn-commit` ya correcto
