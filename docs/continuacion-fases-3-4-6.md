# Exclusive Auto Detail — Guía de Continuación para OpenCode
### Fases 3, 4 y 6 — Plan de ejecución detallado

> Este documento es la continuación operativa de `docs/design-system.md` y `docs/design-tokens.md`. No redefine nada del sistema de diseño — solo secuencia el trabajo que falta, en el orden correcto, con el prompt exacto para cada paso y el criterio de aceptación de cada uno.
>
> **Regla para quien ejecuta esto (Kimi u otro modelo):** cada paso de esta guía es una unidad de trabajo independiente. No avanzar al siguiente paso sin que el anterior esté confirmado. No mezclar dos pasos en un mismo prompt, aunque parezcan relacionados.

---

## 0. Estado actual (referencia rápida)

| Fase | Estado |
|------|--------|
| 1. Tokens | ✅ Completo |
| 2. Componentes base (CSS) | ✅ Completo |
| 3. Login/Landing | 🟡 Parcial — CSS de componentes existe, templates no lo usan |
| 4. Wizard | 🟡 Parcial — CSS tokenizado, HTML no usa componentes |
| 5. Admin | ✅ Completo |
| 6. Pulido | 🟡 Iniciado — clases listas, sin aplicar a templates |

**Diagnóstico de lo que falta:** en las Fases 3 y 4, el trabajo pesado de tokens y componentes ya está hecho (Fases 1 y 2), pero **los HTML todavía apuntan a clases viejas** (`.wizard-card`, `.btn-nav`, clases propias de `login.html`) en lugar de las nuevas (`.ead-card`, `.btn-primary`, `.ead-input`). Esto es lo más importante a entender antes de seguir: **no hay que crear CSS nuevo, hay que migrar HTML para que use el CSS que ya existe.** Si en algún paso de esta guía Kimi propone crear una clase nueva en vez de reutilizar una de `components.css`, es una señal de alerta — hay que frenar y revisar por qué la clase existente no le alcanza.

---

## 1. Principio de secuenciación

El orden de esta guía no es arbitrario. Sigue esta lógica:

1. **Primero lo más aislado y de menor riesgo** (Login) — pantalla pequeña, sin lógica de negocio compleja, sirve como "piloto" para validar que la migración de clases funciona bien antes de tocar el flujo que genera ingresos.
2. **Después la Landing** — más contenido, pero sigue siendo de solo lectura, sin formularios críticos.
3. **Después el Wizard, dividido por paso** (1 al 5) — es el módulo de mayor riesgo funcional, por eso se migra paso por paso y no de una vez.
4. **Recién al final, el Pulido transversal** (micro-interacciones, toasts, detalles de motion) — porque estos detalles solo tienen sentido aplicados sobre componentes que ya están migrados. Pulir un componente viejo que se va a reemplazar es trabajo perdido.

---

## 2. FASE 3 — Login y Landing

### 2.1 Paso: Login

**Objetivo:** que `login.html` deje de tener su propio sistema de estilos aislado y use `components.css` + `tokens.css` como cualquier otra pantalla del producto.

**Prompt para Kimi:**
> "Migrá `login.html` para que use el sistema de componentes existente. Reemplazá el bloque `<style>` embebido y las clases propias (`.login-card`, `.btn-submit`, inputs con estilos inline) por: `.ead-card` para el contenedor del formulario, `.ead-input` para los campos de email y contraseña, `.btn-primary` para el botón 'Ingresar', y las clases de alerta ya definidas en `components.css` para los mensajes flash (`alert-danger`, `alert-success`, `alert-info`). Importá `tokens.css` y `components.css` en el `<head>` en vez de mantener estilos propios. No cambies la estructura del formulario, los `name` de los inputs, ni la lógica de Jinja (`{{ url_for(...) }}`, `{% with messages %}`). Solo el sistema visual."

**Puntos de atención específicos para este paso:**
- `login.html` hoy usa `-apple-system, BlinkMacSystemFont...` como fuente — al importar `tokens.css` esto debe resolverse automáticamente a Montserrat vía la variable `--font-family`. Verificar que efectivamente cambie.
- Los colores de alerta hardcodeados en el `<style>` actual (`rgba(220, 53, 69, 0.15)` para danger, `rgba(25, 135, 84, 0.15)` para success, `rgba(13, 202, 240, 0.15)` para info) deben desaparecer y reemplazarse por las variantes tonales de badges/alertas ya definidas en `components.css` (`--color-danger`, `--color-success`, con su tratamiento tonal correspondiente). Si `components.css` no tiene todavía una clase de alerta con estos tres estados, ese es el primer sub-paso: crearla ahí (en `components.css`, no en `login.html`) y después consumirla.

**Criterio de aceptación:**
- `login.html` no tiene ningún `<style>` con hex hardcodeado propio.
- El botón "Ingresar" es visualmente idéntico a cualquier `.btn-primary` del resto del producto (mismo alto, mismo radio, mismo comportamiento de hover/active).
- La tipografía es Montserrat, no la fuente de sistema.

---

### 2.2 Paso: Colores de marca de redes sociales (excepción documentada)

Antes de seguir con la Landing, hay que resolver un caso pendiente que quedó abierto: `styles.css` retiene hex de Instagram (`#f09433`), TikTok (`#ff0050`), WhatsApp (`#25d366`) y Facebook (`#1877f2`).

**Decisión de diseño (para que quede zanjado y no se re-discuta cada vez):** estos colores **quedan como excepción intencional**, porque no son colores de decisión de marca propia — son identidad de terceros regulada por esas empresas, y cambiarlos rompería el reconocimiento del ícono. La regla de "cero hex fuera del sistema" no aplica a colores de marca de terceros usados exclusivamente en íconos de redes sociales.

**Prompt para Kimi:**
> "En `tokens.css`, agregá un bloque separado y claramente comentado de 'Colores de marca de terceros — excepción documentada, no forman parte de la paleta del sistema': `--color-brand-instagram: #f09433`, `--color-brand-tiktok: #ff0050`, `--color-brand-whatsapp: #25d366`, `--color-brand-facebook: #1877f2`. Reemplazá los hex hardcodeados en `styles.css` que correspondan a estos usos (íconos de redes sociales) por estas variables. No toques ningún otro hex de `styles.css` en este paso — este paso es exclusivamente sobre íconos sociales."

Esto evita dos problemas: que Kimi reinterprete la regla "cero hex" de forma demasiado estricta y trate de recolorear un ícono de WhatsApp con el azul de marca (error real que puede pasar), y que el hex quede suelto sin ninguna trazabilidad en el sistema de tokens.

Los colores de feedback JS de `login.html` (`#9bddb0`, `#f5a3a3`, `#9eeaf9`) **no** son excepción — esos ya deberían haber quedado resueltos en el paso 2.1 al migrar las alertas a las clases semánticas de `components.css`. Verificar que no hayan quedado colgados.

---

### 2.3 Paso: Landing (`index.html` y templates asociados vía `base.html`)

**Objetivo:** aplicar tipografía, espaciado y componentes del sistema a la landing pública sin alterar su estructura de contenido ni su jerarquía de secciones.

**Prompt para Kimi:**
> "Migrá `index.html` (y cualquier template que extienda `base.html` usado en la landing pública, como `servicios.html`) para usar los componentes de `components.css` y los tokens de `tokens.css`. Específicamente: todo botón de acción (`Reservar Turno`, CTAs de sección) debe usar `.btn-primary`; las cards de servicios en `servicios.html` deben migrar de las clases genéricas de Bootstrap (`card`, `card-body`, `card-title`) con estilos inline (`style='background:var(--bg-card)...'`) a `.ead-card`; los badges `bg-warning text-dark` y `bg-info text-dark` deben migrar a las clases semánticas de badge ya definidas (`badge-warning`, `badge-brand` o equivalente). El bloque de 'No hay servicios disponibles' en `servicios.html` debe migrar al componente de empty state definido en `components.css`, no quedar como texto suelto centrado. No cambies el contenido, copy, ni estructura de secciones de la landing — solo el sistema visual y los componentes."

**Puntos de atención:**
- La landing es el único lugar donde el documento de diseño permite algo más de "dinamismo visual" (fotografía, sensación editorial) — esto no es una licencia para introducir estilos nuevos fuera del sistema, es una nota de tono/contenido, no de componentes. La grilla de fotos de trabajos realizados puede tener su propio tratamiento de imagen, pero los botones, cards y badges de la landing usan exactamente los mismos componentes que el resto del producto.
- Revisar que `servicios.html` no siga dependiendo de clases de Bootstrap con estilos inline mezclados (`style="background:var(--bg-card);color:var(--text-light);"` dentro de un `class="card h-100 border-0"`) — esa mezcla es justamente el patrón que el sistema busca eliminar.

**Criterio de aceptación:**
- Ningún `style="..."` inline con `var(--bg-card)` o hex suelto en los templates públicos.
- El botón principal de la landing es visualmente indistinguible de un `.btn-primary` de cualquier otra pantalla.
- El empty state de "sin servicios" tiene ícono/ilustración + mensaje + (si aplica) acción, según la especificación de `design-system.md`.

---

## 3. FASE 4 — Wizard (migración por paso, no de una vez)

Esta es la fase de mayor riesgo. La estrategia es migrar **un paso del wizard a la vez**, verificar que ese paso funcione end-to-end (visual y funcionalmente) antes de tocar el siguiente. No se migra `wizard-*.js` ni la lógica de `WizardState` en ningún momento de esta fase — es exclusivamente CSS/HTML.

### 3.1 Paso previo obligatorio: mapa de clases viejas → nuevas

Antes de tocar un solo template, hay que tener claridad de la equivalencia. Este paso no modifica ningún archivo, solo produce un documento de referencia.

**Prompt para Kimi:**
> "Sin modificar ningún archivo todavía, generá un documento `docs/wizard-migration-map.md` que liste cada clase CSS propia del wizard actualmente en uso en `nueva.html` y sus estilos asociados en `wizard.css` (por ejemplo `.wizard-card`, `.btn-nav`, `.service-card`, `.chip`, `.date-chip`, `.slot-chip`, etc.), y proponga a qué clase de `components.css` corresponde cada una (`.ead-card`, `.ead-select-card`, `.btn-primary`, `.btn-secondary`, `.badge-*`, etc.). Si alguna clase del wizard no tiene equivalente directo en `components.css` porque representa un patrón nuevo (por ejemplo el chip de horario con estados 'disponible/no disponible/seleccionado'), marcala explícitamente como 'requiere extensión del sistema' en vez de forzar una equivalencia que no corresponde."

**Por qué este paso importa:** evita que Kimi improvise una equivalencia forzada a mitad de la migración de un paso del wizard, y te da a vos un punto de revisión barato (leer un `.md`) antes de que se toque código real.

Revisá este documento vos mismo. Si aparecen "requiere extensión del sistema", decidí ahí si:
(a) el componente ya existe pero con otro nombre y hay que corregir el mapeo, o
(b) es un componente genuinamente nuevo (ej. el chip de horario con 3 estados) que hay que diseñar como extensión — en ese caso, ese componente nuevo se define primero en `components.css` siguiendo los mismos principios del Design System (superficie por tono, no por borde; radios de la escala de 3 valores; etc.) antes de usarse en el HTML.

---

### 3.2 Paso: Migrar Paso 1 del wizard (Servicio)

**Prompt para Kimi:**
> "Usando `docs/wizard-migration-map.md` como referencia, migrá exclusivamente el markup correspondiente al Paso 1 del wizard (`paso-1` en `nueva.html`, más los estilos asociados en `wizard.css` que correspondan solo a este paso: cards de paquete, acordeón de categorías, pills de nivel de suciedad, chips de adicionales). Reemplazá las clases propias por las de `components.css` según el mapeo. No toques ningún otro paso del wizard en este prompt. No modifiques `wizard-rendering.js` ni ningún archivo JS — si el JS referencia una clase CSS por nombre (por ejemplo para aplicar/quitar un estado 'seleccionado'), avisame explícitamente cuál JS depende de qué clase antes de renombrarla, no la renombres silenciosamente."

**Esto último es crítico.** Repetilo en cada paso de esta sección. El riesgo real de esta fase no es visual, es que un `wizard-rendering.js` o `wizard-validations.js` haga `classList.contains('service-card-selected')` o similar, y si Kimi renombra la clase en el CSS/HTML sin avisar, la selección visual se rompe en producción aunque el CSS esté "perfecto". Cada prompt de migración de paso debe incluir esta advertencia.

**Verificación manual tuya después de este paso:** abrí el wizard, llegá al Paso 1, seleccioná un paquete, un nivel de suciedad y un adicional. Confirmá que el estado seleccionado se ve (glow + fondo tonal, como define el sistema) y que nada dejó de funcionar.

---

### 3.3 Paso: Migrar Paso 2 (Vehículo)

**Prompt para Kimi:**
> "Mismo criterio que el paso anterior: migrá exclusivamente el markup y estilos del Paso 2 del wizard (`paso-2`): autocomplete de marca/modelo, banner de 'encontrado en el catálogo', grid de tipo de vehículo, grid de tamaño. Usá `.ead-select-card` para las cards de tipo/tamaño con `aspect-ratio` consistente según la especificación (evitar alturas dispares por texto que hace wrap). El banner verde de catálogo debe usar el tratamiento tonal de éxito ya definido en `components.css`, no un verde hardcodeado propio. Avisame si algún JS depende de las clases que voy a renombrar antes de tocarlas."

**Verificación manual:** probá tanto el caso "vehículo reconocido" (ej. Toyota Hiace) como el caso "no reconocido, selección manual" (ej. modelo no catalogado) — son dos layouts distintos dentro del mismo paso y ambos tienen que quedar bien.

---

### 3.4 Paso: Migrar Paso 3 (Fecha y Hora)

**Prompt para Kimi:**
> "Migrá el markup y estilos del Paso 3 (`paso-3`): tabs 'Hoy/Mañana/Elegir fecha' y grid de horarios. Los tabs deben usar un tratamiento tipo segmented-control con `flex:1` cada uno, según la especificación de `design-system.md` (sección STEPPER/navegación de tabs). Para los chips de horario: si `docs/wizard-migration-map.md` marcó este componente como 'requiere extensión del sistema', implementalo ahora en `components.css` como una extensión nueva (`.chip-slot` o similar) con 3 estados — disponible (fondo tonal neutro), seleccionado (fondo tonal de marca), no disponible (opacidad reducida, no clickeable) — usando exclusivamente variables de `tokens.css`, sin colores nuevos fuera de la paleta. Eliminá cualquier uso de naranja/ámbar en los horarios que no represente una advertencia real (ese color queda reservado para `--color-warning` semántico, no para indicar disponibilidad)."

**Este es el paso donde se resuelve** el problema detectado en la auditoría original: los horarios en azul/naranja sin leyenda. Verificá específicamente que después de este paso, el color de los horarios tenga un único significado consistente.

---

### 3.5 Paso: Migrar Paso 4 (Datos personales)

**Prompt para Kimi:**
> "Migrá el markup del Paso 4 (`paso-4`): todos los inputs (nombre, apellido, teléfono, email, cédula) deben usar `.ead-input` con label siempre visible arriba, según la especificación. Implementá el estado de validación en tiempo real para el campo de teléfono usando el patrón definido en `design-system.md` (ícono discreto a la derecha del campo, nunca cambio de color del texto ingresado). Agregá normalización automática de capitalización (Title Case) en nombre y apellido al perder foco del input — esto es JS mínimo y puntual, no forma parte del refactor de CSS, así que aplicalo como una función aislada en `wizard-validations.js` o `wizard-main.js`, la que ya maneje `collectFormData()`, sin tocar el resto de la lógica de ese archivo."

**Nota:** este es el único paso de la Fase 4 que toca JS deliberadamente (la normalización de capitalización), porque es un fix puntual identificado en la auditoría original, no parte del refactor visual. Está bien que sea una excepción explícita — lo importante es que sea la única y esté señalada como tal en el prompt.

**Verificación manual:** escribí un nombre en minúscula/mayúscula mezclada como en la captura original ("eLIAS") y confirmá que al salir del campo se normaliza a "Elias".

---

### 3.6 Paso: Migrar Paso 5 (Confirmación)

**Prompt para Kimi:**
> "Migrá el markup del Paso 5 (`paso-5`): la card de resumen debe usar el componente RESUMEN definido en `design-system.md` (labels en `--text-overline`, valores en `--text-body-strong`, línea divisoria sutil entre filas, cada fila con affordance de tap-to-edit). El botón 'Confirmar Reserva' debe usar `.btn-primary` pero con la excepción de altura documentada (52px en vez de 48px) para reflejar que es la acción de mayor compromiso del flujo. Si el precio total todavía no se muestra en esta pantalla (pendiente detectado en la auditoría original), agregalo como una fila adicional en el resumen, con mayor tamaño/peso que el resto de las filas — pero no inventes de dónde sale ese dato: decime primero si `WizardState.precio` ya tiene el valor final calculado disponible en este punto del flujo, antes de tocar el HTML."

**Importante:** esta última instrucción evita que Kimi "invente" un campo de precio con un valor hardcodeado o mal calculado solo para que se vea bien. Si el dato no está disponible en el estado del wizard en este punto, es una pregunta legítima para vos, no algo que Kimi deba resolver solo.

---

### 3.7 Paso: Empty states y skeleton loading en el wizard

**Prompt para Kimi:**
> "Con los 5 pasos del wizard ya migrados, agregá los skeleton loading states definidos en `components.css` a los momentos donde el wizard espera datos de red: carga inicial de servicios/tipos/segmentos en `wizard-main.js` → `WizardMain.init()`, y carga de slots de horario en `wizard-availability.js`. Mientras estos datos cargan, mostrar el skeleton correspondiente a la forma del contenido (cards de servicio, grid de horarios) en vez de dejar el espacio vacío o mostrar solo el texto 'Calculando...'. Esto es principalmente HTML/CSS — para el JS, solo agregar el toggle de clase que muestra/oculta el skeleton en el punto donde ya existe el fetch, sin modificar la lógica de fetch en sí."

**Verificación manual:** simulá conexión lenta (throttling en devtools) y confirmá que se ve un skeleton coherente con la forma del contenido, no una pantalla vacía ni un salto brusco.

---

## 4. FASE 6 — Pulido (aplicación final, después de que 3 y 4 estén cerradas)

Este orden importa: pulir un componente que todavía usa clases viejas es trabajo que se pierde apenas se migra esa clase. Por eso el Pulido va al final, no en paralelo.

### 4.1 Micro-interacciones sobre templates ya migrados

**Prompt para Kimi:**
> "Sobre los templates ya migrados a componentes del sistema (login, landing, wizard completo, admin), aplicá las clases de micro-interacción ya definidas en `components.css` (press effect en `:active`, focus-visible, badge/flash/modal entry animations) a todos los elementos interactivos: botones, chips, cards seleccionables, inputs. No crear ninguna animación nueva — usar exclusivamente lo que ya existe en `components.css` de la Fase 6 previa. Si encontrás un elemento interactivo que no tiene ninguna de estas clases aplicadas, agregala; si encontrás un elemento con una animación propia hecha ad-hoc, reemplazala por la clase del sistema."

### 4.2 Sistema de toast/notificaciones

Esto todavía no existe como componente, hay que definirlo antes de aplicarlo.

**Prompt para Kimi:**
> "Diseñá e implementá un componente de toast en `components.css`, siguiendo la especificación de `design-system.md` (sección TOASTS): entrada rápida desde arriba o abajo, salida más lenta, máximo 2 visibles a la vez con reemplazo del más antiguo por transición de cruce. Variantes tonales: éxito, error, info — reusando `--color-success`, `--color-danger`, `--color-brand`. Implementalo como un componente JS mínimo y genérico (`showToast(mensaje, tipo)`) en un archivo nuevo `static/js/toast.js`, sin dependencias externas. Después, reemplazá los `showBanner(mensaje)` actuales del wizard (en `wizard-main.js`, al fallar el submit de la reserva) por este nuevo sistema de toast."

**Verificación manual:** forzá un error de submit en el wizard (por ejemplo un campo inválido) y confirmá que aparece como toast, no como el banner anterior.

### 4.3 Detalles "Apple-level" (checks, transiciones, price counting)

**Prompt para Kimi:**
> "Aplicá los siguientes detalles puntuales, cada uno como una unidad de trabajo separada — confirmame cada uno antes de seguir con el siguiente:
> 1. Animación de aparición del check de selección (cards de tipo de vehículo, tamaño) con el efecto de 'asentado con leve rebote' (`cubic-bezier(0.34, 1.56, 0.64, 1)`) definido en el motion system.
> 2. Transición de conteo suave cuando el precio se recalcula en el wizard (al agregar/quitar un adicional), en vez de reemplazo instantáneo del número.
> 3. Transición entre pasos del wizard ajustada a 220-240ms con la curva estándar del sistema, en vez del fade de 120ms actual.
> No apliques los tres al mismo tiempo — hacé uno, mostrame el resultado, y seguimos con el próximo."

### 4.4 Sidebar mobile overlay (admin) — testing, no desarrollo

Este ítem pendiente no es una tarea de código nueva, es una verificación de algo que ya debería existir.

**Prompt para Kimi:**
> "Revisá el comportamiento del sidebar del admin en viewport mobile (menor a 768px). Confirmame: ¿el sidebar se convierte en un overlay que se abre/cierra, o queda siempre visible empujando el contenido? Si ya existe la lógica de overlay, verificá que el fondo se oscurezca con la transición de opacidad simultánea a la aparición del sidebar (no después, como indica la especificación de bottom sheet/overlay del design system), y que cerrar el overlay tocando afuera funcione. Si no existe overlay todavía, no lo implementes sin que yo lo confirme primero — es un cambio de comportamiento, no solo visual."

### 4.5 Focus-visible en todos los templates

**Prompt para Kimi:**
> "Verificá que la clase de `focus-visible` definida en `components.css` esté efectivamente aplicándose a todos los elementos interactivos (botones, inputs, links, chips, cards seleccionables) en los 4 módulos del producto (público, wizard, admin, login), navegando cada pantalla exclusivamente con teclado (Tab). Listame cualquier elemento donde el foco no sea visible o donde aparezca el outline azul genérico del navegador en vez del halo del sistema."

---

## 5. Orden de ejecución resumido

Ejecutar en este orden exacto, sin saltar pasos:

1. Login (2.1)
2. Excepción de colores de marca de terceros (2.2)
3. Landing (2.3)
4. Mapa de migración del wizard (3.1) — **revisar vos antes de continuar**
5. Wizard Paso 1 (3.2)
6. Wizard Paso 2 (3.3)
7. Wizard Paso 3 (3.4)
8. Wizard Paso 4 (3.5)
9. Wizard Paso 5 (3.6)
10. Skeletons/empty states del wizard (3.7)
11. Micro-interacciones sobre todo lo migrado (4.1)
12. Sistema de toast (4.2)
13. Detalles Apple-level, uno por uno (4.3)
14. Testing de sidebar mobile (4.4)
15. Auditoría de focus-visible (4.5)

## 6. Checklist final antes de dar el proyecto por cerrado

- [ ] Cero hex fuera de `tokens.css`, salvo la excepción documentada de colores de redes sociales.
- [ ] Un solo azul de marca (`--color-brand`) en todo el proyecto — sin excepción.
- [ ] Todos los botones del producto (público, wizard, admin, login) son `.btn-primary`, `.btn-secondary` o `.btn-danger` — cero clases de botón propias sobrevivientes.
- [ ] Todos los inputs son `.ead-input` con el mismo alto, padding y comportamiento de foco.
- [ ] El precio total es visible antes de confirmar una reserva.
- [ ] Ningún paso del wizard tiene espacio vacío estructural post-CTA (footer sticky en los 5 pasos).
- [ ] El color naranja/ámbar solo aparece como advertencia real, en ningún otro contexto.
- [ ] Los 5 pasos del wizard fueron probados manualmente end-to-end después de la migración, incluyendo el caso de vehículo no catalogado.
- [ ] El sistema de toast reemplazó completamente al banner anterior del wizard.
- [ ] Navegación completa por teclado (Tab) es posible y visible en las 4 zonas del producto.