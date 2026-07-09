
/
Claude terminó la respuesta

Identificó inconsistencias visuales y planificó auditoría de diseño integral
Identificó inconsistencias visuales y planificó auditoría de diseño integral
Suficiente evidencia. Ya tengo el panorama completo del sistema. Voy a exponer el diagnóstico y luego el Design System v1.

Diagnóstico: ¿es un solo producto?
No. Al inspeccionar styles.css, wizard.css, base_admin.html y login.html en conjunto, hay evidencia concreta de que cada módulo fue construido de forma aislada:

1. Tokens duplicados y divergentes, no compartidos
styles.css define un :root con las variables de marca. Pero base_admin.html no importa styles.css — copia y pega el mismo :root dentro de un <style> embebido en el propio HTML. Hoy los valores coinciden por casualidad, pero es una fuente de verdad duplicada: cualquier cambio de marca requiere editarlo en dos lugares, y ya hay micro-derivas (--bg-secondary: #111111 en un archivo vs #111 en el otro — mismo color, sintaxis distinta, cero trazabilidad).

2. Azul de marca inconsistente entre módulos
Sitio público / admin (styles.css, base_admin.html): --accent: #1a6bff
Wizard (wizard.css): usa 
#3b82f6 y 
#2563eb como azules de selección — un azul completamente distinto, no una variable, hardcodeado directo.
Esto significa que si un usuario navega de la landing (azul 
#1a6bff) al wizard de reserva (azul 
#3b82f6), el color "de marca" cambia de tono sin ninguna razón. Es el hallazgo más grave de toda la auditoría: la marca no tiene un azul, tiene dos.

3. Login.html vive fuera del sistema por completo
login.html no importa styles.css, no usa Montserrat (usa -apple-system, BlinkMacSystemFont... — la fuente del sistema operativo), y hardcodea sus propios hex (
#0d0d0d, 
#1a6bff, 
#1a1a1a) que coinciden con el sistema por copia manual, no por herencia. Es una página que "se parece" al producto por imitación visual, no por arquitectura compartida.

4. Border-radius: 11 valores distintos en styles.css, 8 en wizard.css, sin superposición clara
50%, 20px, 16px, 12px, 10px, 8px, 6px, 5px, 4px, 2px, 0 en un archivo; 20px, 18px, 12px, 8px, 3px, 2px, 0, 50% en el otro. No hay una escala — hay "lo que pareció bien en el momento" cada vez que se escribió una regla.

5. Dos sistemas de botones que no se comunican
styles.css tiene .btn-primary-custom / .btn-outline-custom con padding 0.85rem 2rem. wizard.css construye sus propios botones con clases distintas y otro padding. base_admin.html tiene un tercer set (.btn-sm-custom). Tres vocabularios de botón para un mismo producto.

6. Spacing sin escala
Los padding de styles.css van de 0.15rem a 3rem pasando por 0.2, 0.25, 0.38, 0.4, 0.5, 0.6, 0.65, 0.75, 0.85, 1.1, 1.2, 1.25, 1.5, 1.75, 2, 2.2, 2.5... — no es una escala, es un historial de decisiones puntuales acumuladas.

7. Iconografía mixta
wizard.css importa Font Awesome ('Font Awesome 6 Free') mientras el wizard en las capturas usa además íconos SVG custom sueltos para tipos de vehículo. El sitio público (servicios.html) también usa Font Awesome pero para íconos completamente distintos en propósito (fa-circle-info). No hay un set único ni una decisión sobre outline vs. solid.

Design System v1 — Exclusive Auto Detail
0. Principio rector
Una sola fuente de verdad. Todo módulo (público, wizard, admin, auth) debe consumir el mismo archivo de tokens. Ningún componente vuelve a hardcodear un color, radio, sombra o espaciado que ya exista como variable. Si un valor no está en este documento, no se usa — se propone como adición al sistema primero.

1. Color
1.1 Paleta base (única, sin excepciones)
--color-bg-0:        #0A0A0C   /* fondo base de toda superficie de app */
--color-bg-1:        #16161A   /* tarjetas, paneles */
--color-bg-2:        #1E212C   /* elementos activos/hover, tinte frío */
--color-border:       rgba(255,255,255,0.08)   /* único borde permitido en todo el sistema */

--color-brand:        #1A6BFF   /* ÚNICO azul de marca — reemplaza #3b82f6 y #2563eb en wizard.css */
--color-brand-hover:  #1557D9
--color-brand-tint:   rgba(26,107,255,0.14)    /* fondos tonales de selección */
--color-brand-glow:   rgba(26,107,255,0.35)    /* box-shadow de foco/selección */

--color-gold:         #D4A843   /* uso exclusivo: marca/logo y detalles premium puntuales, nunca como color funcional */

--color-text-primary:   #F5F5F7
--color-text-secondary: #A0A0A0
--color-text-tertiary:  #6B6B70

--color-success:      #2FB768
--color-warning:       #E0A429
--color-danger:        #E5484D
Regla dura: 
#3b82f6, 
#2563eb, 
#1a6bff escrito a mano, #ccc, #111, o cualquier hex fuera de esta lista quedan prohibidos en cualquier archivo del proyecto. Todo color se referencia por variable, siempre.

Regla de uso del dorado: --color-gold no es un color de sistema (no se usa en botones, estados, badges funcionales). Es exclusivamente de identidad: logo, encabezados heroicos puntuales. Mezclarlo con azul como "acento secundario" funcional (como ocurre hoy en detalles sueltos) diluye cuál es el color de acción del producto.

1.2 Estados semánticos — un solo significado por color
Azul (--color-brand) = selección, acción primaria, foco. Nunca se usa para otra cosa.
Verde (--color-success) = confirmación, disponibilidad, éxito.
Ámbar (--color-warning) = advertencia real (ej. "vehículo no catalogado"). No se usa nunca como decoración o para indicar "recomendado" — eso se resuelve con azul.
Rojo (--color-danger) = error de validación o irreversibilidad (cancelar, eliminar).
Ningún color puede tener dos significados en el mismo producto (hoy el ámbar aparece como warning en el Paso 2 del wizard y también sin explicación en los horarios del Paso 3 — mismo color, significados distintos: eso queda eliminado).

2. Tipografía
2.1 Familia única
--font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
login.html deja de usar el stack de sistema operativo y pasa a Montserrat, igual que el resto del producto. La tipografía es la firma más barata y más visible de que "todo es la misma marca" — hoy es el único módulo que rompe esto.

2.2 Escala tipográfica (única para todo el proyecto)
--text-overline:   11px / 600 / +0.08em / uppercase   → labels de sección, "PASO X DE 5"
--text-caption:     13px / 500 / 0                     → labels de campo, texto auxiliar
--text-body:        15px / 400 / 0                     → párrafos, descripciones
--text-body-strong: 15px / 600 / 0                     → valores de datos, ítems de lista
--text-title-sm:    17px / 700 / 0                     → títulos de tarjeta (paquete, servicio)
--text-title-md:    22px / 700 / -0.01em                → títulos de sección (H2 dentro de página)
--text-title-lg:    32px / 900 / -0.02em                → hero, títulos de landing
No existen tamaños intermedios inventados (0.85rem, 0.95rem, 1.1rem sueltos que hoy aparecen en login.html y en distintos puntos de styles.css). Todo tamaño de texto en el proyecto mapea a una de estas 7 categorías.

3. Espaciado
3.1 Escala 4pt estricta
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 24px
--space-6: 32px
--space-7: 48px
--space-8: 64px
Prohibido usar valores en rem sueltos como 0.15rem, 0.38rem, 0.65rem, 0.85rem, 1.1rem, 1.75rem (todos presentes hoy en styles.css). Cualquier padding/margin del proyecto debe resolver a uno de los 8 valores de arriba. Si ninguno "queda bien", el problema es del layout, no del espaciado — se ajusta la estructura, no se inventa un valor nuevo.

3.2 Aplicación estándar
Padding interno de card: --space-4 (16px)
Padding interno de card grande (hero, panel de resumen): --space-5 (24px)
Gap entre elementos de un grupo (chips, botones inline): --space-2 (8px)
Gap entre secciones de una página/paso: --space-5 (24px)
Márgenes laterales de contenedor en mobile: --space-5 (20-24px, fijo en todos los templates)
4. Radios
4.1 Solo 3 valores en todo el proyecto
--radius-sm:   8px    → inputs, chips, badges rectangulares
--radius-md:   14px   → cards, paneles, modales, banners de estado
--radius-full: 999px  → pills, avatares, tabs tipo segmented-control
Elimina: 2px, 3px, 4px, 5px, 6px, 10px, 12px, 16px, 18px, 20px — todos actualmente en uso en algún archivo del proyecto sin criterio. 50% se mantiene solo para elementos circulares reales (avatares, iconos contenedor).

5. Elevación (bordes y sombras)
5.1 Jerarquía de superficies (reemplaza el uso de bordes de 1px como método de diferenciación)
Nivel 0 (fondo):        --color-bg-0, sin sombra
Nivel 1 (card default): --color-bg-1, sin sombra, sin borde
Nivel 2 (card hover/interactiva): --color-bg-1 + box-shadow: 0 2px 8px rgba(0,0,0,0.24)
Nivel 3 (card seleccionada):      --color-bg-2 + box-shadow: 0 0 0 1.5px var(--color-brand), 0 4px 16px var(--color-brand-glow)
Nivel 4 (modal/overlay flotante): --color-bg-1 + box-shadow: 0 12px 32px rgba(0,0,0,0.5)
Regla dura: ningún componente usa border: 1px solid como único diferenciador visual salvo --color-border para separar zonas estáticas (ej. sidebar del admin). Selección, foco y jerarquía se comunican con sombra/tinte, no con líneas.

6. Componentes
6.1 Botones — un solo sistema, tres variantes, en todo el proyecto (público, wizard, admin, auth)
.btn-primary
  background: var(--color-brand)
  color: #fff
  height: 48px
  padding: 0 var(--space-5)
  border-radius: var(--radius-sm)
  font: var(--text-body-strong)
  hover: background var(--color-brand-hover)
  active: scale(0.98)

.btn-secondary
  background: rgba(255,255,255,0.06)   /* nunca borde */
  color: var(--color-text-primary)
  mismas dimensiones que .btn-primary

.btn-danger
  background: var(--color-danger)
  reservado para eliminar/cancelar, uso restringido
Elimina .btn-primary-custom, .btn-outline-custom, .btn-sm-custom, .btn-nav, y cualquier botón propio del wizard — todos migran a estas 3 clases. Un botón "Confirmar Reserva" (compromiso final) puede usar .btn-primary con height: 52px como única excepción documentada de tamaño, no de sistema.

6.2 Inputs — mismo componente en login, wizard, admin y filtros
height: 48px
padding: 0 var(--space-4)
background: var(--color-bg-1)
border: 1px solid var(--color-border)
border-radius: var(--radius-sm)
color: var(--color-text-primary)
placeholder: var(--color-text-tertiary)

:focus → border-color: var(--color-brand) + box-shadow: 0 0 0 3px var(--color-brand-glow)
Hoy login.html define sus propios inputs con padding: 0.75rem 1rem y radio 8px por coincidencia, no por sistema; base_admin.html usa otro padding para .filtros-admin input. Todo input del proyecto —autenticación, wizard, panel admin— se resuelve con esta única especificación.

6.3 Cards de selección (paquetes, tipo de vehículo, servicios)
padding: var(--space-4)
border-radius: var(--radius-md)
background: var(--color-bg-1)
default: sin sombra
hover: Nivel 2
seleccionada: Nivel 3
min-height: 88px, aspect-ratio consistente dentro del mismo grid
6.4 Badges / estados (chips "2 días", "Requiere inspección previa", etc.)
padding: 4px 10px
border-radius: var(--radius-full)
font: var(--text-overline) pero sin uppercase forzado si el texto ya lo es
background tonal según semántica: 
  info    → var(--color-brand-tint) + texto var(--color-brand)
  warning → rgba(224,164,41,0.14) + texto var(--color-warning)
  success → rgba(47,183,104,0.14) + texto var(--color-success)
servicios.html hoy usa badge bg-warning text-dark y badge bg-info text-dark — clases genéricas de Bootstrap con colores que no pertenecen a la paleta del proyecto. Migran a estas variantes tonales.

6.5 Alertas / mensajes flash (login, formularios)
Mismo tratamiento tonal que los badges, pero a nivel de bloque:

padding: var(--space-3) var(--space-4)
border-radius: var(--radius-sm)
sin borde — reemplazar border: 1px solid rgba(...) actual por solo background tonal
7. Iconografía
Un solo set: Font Awesome 6 (ya está disponible en admin y wizard) se convierte en el set oficial único. Se eliminan los SVG custom sueltos del wizard para tipo de vehículo — se reemplazan por equivalentes de Font Awesome o, si no existen, se ilustra un set custom con el mismo stroke-width que el resto (1.5px, nunca mezclado con Font Awesome solid en la misma pantalla).
Contenedor obligatorio: todo ícono funcional (no decorativo) vive dentro de un contenedor de 40×40px, background: rgba(255,255,255,0.05), border-radius: var(--radius-sm). Nunca flota suelto sobre el fondo.
El dorado (--color-gold) nunca tiñe un ícono funcional — queda reservado a marca.
8. Estados de interacción (unificados)
Estado	Tratamiento
:hover (elemento clickeable)	Nivel 2 de elevación, sin cambio de color de texto salvo en links
:active (tap/click)	transform: scale(0.98), 80ms
:focus-visible	box-shadow: 0 0 0 3px var(--color-brand-glow), nunca outline genérico del navegador salvo como fallback de accesibilidad
:disabled	opacity: 0.4, cursor: not-allowed, sin cambio de color de fondo
seleccionado	Nivel 3 de elevación + --color-brand-tint de fondo si aplica
9. Animación (motion tokens)
--duration-fast:   80ms   → feedback táctil (:active, scale)
--duration-base:   200ms  → transiciones de estado (hover, foco, aparición de badge)
--duration-slow:   240ms  → transición entre pasos/pantallas completas

--easing-standard: cubic-bezier(0.25, 0.1, 0.25, 1)   → la mayoría de las transiciones
--easing-pop:      cubic-bezier(0.34, 1.56, 0.64, 1)   → aparición de checks/badges (con overshoot)
Se elimina cualquier transición ad-hoc definida por archivo (hoy styles.css usa 0.2s, 0.25s, 0.3s indistintamente sin relación entre sí). Todo motion del proyecto usa uno de estos tres tiempos.

10. Gobernanza del sistema
Un solo archivo de tokens (tokens.css o equivalente) importado por styles.css, wizard.css y el <style> embebido de base_admin.html. login.html deja de ser standalone: importa el mismo archivo.
Ningún hex, ningún rem suelto, ningún radio fuera de la escala se permite en nuevas reglas CSS — todo pasa por variable.
Cualquier componente nuevo (ej. un badge que no está en esta spec) se diseña primero como extensión del sistema — no como solución puntual del módulo donde nace, que es exactamente cómo se llegó al estado actual (3 sistemas de botones, 2 azules, 11 radios).
Excelente.
Ahora quiero hacer la última iteración.
Ya conoces completamente el proyecto.
Ya analizaste:
- flujo-reservas.md
- wizard.css
- styles.css
- login.html
- base_admin.html
- capturas del wizard
- capturas del sitio
- capturas del panel
- Design System v1
NO quiero otra auditoría.
NO quiero otro diagnóstico.
Asume que todo eso ya fue aprobado.
Quiero que actúes como Creative Director y Principal Visual Designer.
Tu objetivo es diseñar la versión definitiva de Exclusive Auto Detail.
No pienses como desarrollador.
No pienses como arquitecto.
Piensa como el responsable del diseño de productos de Apple, Linear, Arc Browser, Things 3 y Stripe.
Quiero que el producto se sienta:
- extremadamente limpio
- premium
- moderno
- consistente
- elegante
- rápido
- confiable
NO quiero minimalismo vacío.
Quiero lujo discreto.
No quiero algo llamativo.
Quiero algo refinado.
------------------------------------------------------------
OBJETIVO
Generar una especificación visual completa para OpenCode.
No escribas código.
No escribas CSS.
No escribas HTML.
No hables de implementación.
Solo diseño.
------------------------------------------------------------
Quiero que diseñes:
1. El lenguaje visual definitivo.
2. La personalidad de la interfaz.
3. Qué debe sentir un usuario al usarla.
4. Cómo debe diferenciarse de una aplicación Bootstrap.
5. Qué detalles hacen que una aplicación se perciba premium.
------------------------------------------------------------
Después quiero una especificación componente por componente.
Por ejemplo:
BOTONES
- altura
- sensación
- sombras
- estados
- animaciones
- foco
- disabled
- loading
INPUTS
- altura
- padding
- placeholder
- foco
- validación
- error
- éxito
CARDS
- estructura
- ritmo interno
- jerarquía
- selección
- hover
- active
BADGES
CHIPS
ACCORDIONS
BOTTOM SHEET
SIDEBAR
STEPPER
MODALES
TABLAS
FORMULARIOS
RESUMEN
TOASTS
MENSAJES
ALERTAS
LOADING
EMPTY STATES
ERROR STATES
PÁGINA DE CONFIRMACIÓN
LOGIN
LANDING
PANEL ADMIN
------------------------------------------------------------
Después quiero que diseñes el Motion System.
Especifica:
- duración
- easing
- cuándo animar
- cuándo NO animar
No quiero animaciones porque sí.
Solo las que mejoren la experiencia.
------------------------------------------------------------
Luego quiero un apartado llamado
"Pequeños detalles que hacen que una aplicación se sienta de nivel Apple"
No quiero cambios grandes.
Quiero pequeños detalles.
Ejemplo:
- cómo aparece un check
- cómo desaparece un panel
- cómo cambia un botón
- cómo responde una card al tocarla
- cómo se mueve un badge
- cómo cambia un input válido
- cómo debe sentirse una transición
------------------------------------------------------------
Finalmente quiero una sección llamada
"Implementación"
Pero NO quiero código.
Quiero que dividas absolutamente todo en fases para OpenCode.
Por ejemplo
FASE 1
Tokens
FASE 2
Componentes Base
FASE 3
Landing
FASE 4
Wizard
FASE 5
Admin
FASE 6
Pulido
Cada fase debe indicar:
- prioridad
- impacto visual
- dificultad
- riesgo
- dependencias
------------------------------------------------------------
Quiero que este documento sea la especificación oficial de diseño de Exclusive Auto Detail.
No escribas una auditoría.
Escribe un manual de diseño que un equipo profesional podría utilizar durante años.
Sé extremadamente detallado.
No tengas miedo de escribir un documento muy largo.
La calidad es mucho más importante que la longitud.

Mostrar más

Estructuró documento de diseño visual completo en español
Estructuró documento de diseño visual completo en español
Este documento cierra el ciclo: es la especificación oficial de diseño de Exclusive Auto Detail, pensada para durar. Cubre visión y personalidad, cada componente del sistema, el motion system completo, los micro-detalles de nivel Apple, y las 6 fases de implementación con prioridad/impacto/dificultad/riesgo/dependencias para que OpenCode lo ejecute en orden.


Exclusive auto detail design spec v2
Documento · MD 
yo tengo open code go, cual lenguaje uso de lo que tiene disponible ese


Evaluó modelos disponibles para proyecto Flask y JavaScript
Evaluó modelos disponibles para proyecto Flask y JavaScript
Con OpenCode Go no elegís un "lenguaje" en el sentido de Python/JS/Go — elegís qué modelo vas a usar para que ejecute las tareas. El proyecto en sí sigue siendo Python/Flask + HTML/CSS/JS vanilla, eso no cambia.

Los modelos disponibles hoy en Go son:

GLM-5.2 / GLM-5.1, Kimi K2.7 Code / Kimi K2.6, DeepSeek V4 Pro / V4 Flash, MiniMax M3 / M2.7, Qwen3.7 Max / Plus / 3.6 Plus, MiMo-V2.5 / Pro.

Para tu caso (implementar el Design System v1/v2 sobre un proyecto Flask con HTML+CSS+JS vanilla — muchos archivos, consistencia sistemática, seguir instrucciones de diseño al pie de la letra) yo priorizaría así:

Para las fases 1, 2 y 6 (tokens, componentes base, pulido fino) — acá la precisión y el seguimiento estricto de reglas importa más que la velocidad:

Kimi K2.7 Code — es la variante específicamente entrenada para coding, buen balance costo/calidad, y tu presupuesto de Go te da ~1.350 requests cada 5hs con este modelo.
Alternativa: GLM-5.2 (el flagship de la lista), si sentís que Kimi se equivoca en detalles de CSS/layout.
Para las fases 3, 4 y 5 (landing, wizard, admin — trabajo repetitivo de aplicar el sistema ya definido sobre muchas pantallas) — acá conviene priorizar volumen sobre sofisticación, porque son cambios mecánicos guiados por la spec que ya tenés:

DeepSeek V4 Flash — es barato y rapidísimo (158k requests/mes estimadas), ideal para iterar archivo por archivo sin quemar presupuesto.
Si algo sale mal o necesita más criterio de diseño, subís puntualmente a Kimi K2.7 Code o GLM-5.2 para esa tarea específica.
Para decisiones de arquitectura o revisión de coherencia general del sistema (no tanto para escribir código en bruto):

Qwen3.7 Max — el más caro pero el de mejor razonamiento general de la lista, resérvalo para "revisá si esta implementación respeta el Design System completo" más que para tareas de escritura masiva.
Mi recomendación concreta para empezar: arrancá la Fase 1 (tokens) con Kimi K2.7 Code. Es el punto más sensible — un error ahí se replica en todo el proyecto — y esa variante está pensada exactamente para esto. Después bajás a DeepSeek V4 Flash para las fases de aplicación masiva (3, 4, 5).

uso kimi2.7 y le pego todo ese documento entonces


Deliberó estrategia efectiva para procesar documentos extensos
Deliberó estrategia efectiva para procesar documentos extensos
Sí, pero no lo pegues entero de una sola vez como un mensaje gigante — vas a quemar contexto y el modelo va a intentar hacer todo junto, que es exactamente lo que no querés (la Fase 1 tiene que estar sólida antes de tocar la Fase 2).

Mejor así:

1. Guardá el documento dentro del repo, no en el chat — por ejemplo en docs/design-system.md. Así queda como referencia permanente que OpenCode puede releer cuando lo necesite, en vez de perderse en el historial de la sesión.

2. Corré /init en la raíz del proyecto si todavía no lo hiciste — genera un agents.md con el mapa del repo (rutas, estructura, stack). Esto le da a Kimi contexto real de dónde están wizard.css, styles.css, base_admin.html, etc., sin que tengas que explicárselo cada vez.

3. Trabajá fase por fase, no el documento completo de un tiro. Para la Fase 1, algo como:

"Leé docs/design-system.md, sección PARTE II (color, tipografía, espaciado, radios, sombras, motion tokens). Creá un único archivo de tokens que consolide todo eso. No toques ningún otro archivo todavía — esta fase es solo la definición de tokens."

4. Recién cuando la Fase 1 esté aprobada por vos, seguís con la Fase 2 apuntando al mismo documento:

"Ahora leé la sección de BOTONES, INPUTS y CARDS del mismo documento y construí esos componentes base usando los tokens que ya creamos en la fase anterior."

5. Para las fases 3-5 (landing, wizard, admin), referenciá tanto el documento de diseño como el archivo específico a modificar:

"Aplicá los componentes base de la Fase 2 a login.html, siguiendo la sección LOGIN del design system. No cambies estructura ni lógica, solo estilos."

La razón de dividirlo así: si le tirás las 6 fases juntas, Kimi va a intentar resolver todo en un solo pase gigante, con más probabilidad de inconsistencias entre archivos — justo el problema que el documento está tratando de resolver. Fase por fase, con el .md como fuente de verdad persistente, es como se mantiene la disciplina que definimos.

1783571303220_image.png
?


Identified documentation gap and synthesized consolidated solution
Identified documentation gap and synthesized consolidated solution
Buen catch de Kimi — tiene razón. Pasó esto: el documento final que le diste (la "especificación oficial") habla de los componentes en términos cualitativos ("una escala de 4pt", "3 radios", "un azul de marca") pero los valores numéricos concretos (los hex exactos, el 
#1A6BFF, la escala 4/8/12/16/24/32/48/64, los 3 radios en 8px/14px/999px) están en el Design System v1, que fue una respuesta anterior de este chat — nunca lo guardaste como archivo separado en el repo.

Kimi no está inventando un problema: sin esos valores explícitos, cualquier token que "infiera" o cualquier valor que "extraiga de los CSS actuales" va a ser una interpretación suya, no la especificación que definimos. Y extraer de los CSS actuales sería literalmente lo contrario de lo que buscamos — esos son los archivos con los 11 radios y los 2 azules que estamos corrigiendo.

La respuesta correcta es la opción 3 ("Esperar Design System v1"), pero no te quedes esperando pasivo — dáselo ahora.

Lo que tenés que hacer:

Tomá mi respuesta anterior de este chat titulada "Design System v1" (la que tiene las secciones 1. Color, 2. Tipografía, 3. Espaciado, 4. Radios, 5. Elevación, 6. Componentes) y guardala como un archivo nuevo en el repo, por ejemplo docs/design-tokens.md.
Respondele a Kimi con algo como:
"Esperar Design System v1. Ya lo agregué al repo en docs/design-tokens.md — ese archivo tiene los valores explícitos (hex, escala de espaciado, radios, sombras). Usá docs/design-tokens.md como fuente de los valores numéricos y docs/design-system.md como guía de personalidad/componentes/motion. Empezá la Fase 1 con ambos."

Así Kimi tiene las dos piezas: el documento "definitivo" (Parte II en adelante, que es visión + comportamiento) y el documento con los números duros (que es el que realmente faltaba). Sin el segundo, cualquier cosa que construya hoy va a tener valores inventados que después vas a tener que corregir a mano.



Design System v1 — Exclusive Auto Detail 0. Principio rector Una sola fuente de verdad. Todo módulo (público, wizard, admin, auth) debe consumir el mismo archivo de tokens. Ningún componente vuelve a hardcodear un color, radio, sombra o espaciado que ya exista como variable. Si un valor no está en e

pasted






Claude es IA y puede cometer errores. Por favor, verifica nuevamente las respuestas.











Contenido pegado
10.91 KB •165 líneas
•
El formato puede ser inconsistente con la fuente

Design System v1 — Exclusive Auto Detail
0. Principio rector
Una sola fuente de verdad. Todo módulo (público, wizard, admin, auth) debe consumir el mismo archivo de tokens. Ningún componente vuelve a hardcodear un color, radio, sombra o espaciado que ya exista como variable. Si un valor no está en este documento, no se usa — se propone como adición al sistema primero.

1. Color
1.1 Paleta base (única, sin excepciones)
--color-bg-0:        #0A0A0C   /* fondo base de toda superficie de app */
--color-bg-1:        #16161A   /* tarjetas, paneles */
--color-bg-2:        #1E212C   /* elementos activos/hover, tinte frío */
--color-border:       rgba(255,255,255,0.08)   /* único borde permitido en todo el sistema */

--color-brand:        #1A6BFF   /* ÚNICO azul de marca — reemplaza #3b82f6 y #2563eb en wizard.css */
--color-brand-hover:  #1557D9
--color-brand-tint:   rgba(26,107,255,0.14)    /* fondos tonales de selección */
--color-brand-glow:   rgba(26,107,255,0.35)    /* box-shadow de foco/selección */

--color-gold:         #D4A843   /* uso exclusivo: marca/logo y detalles premium puntuales, nunca como color funcional */

--color-text-primary:   #F5F5F7
--color-text-secondary: #A0A0A0
--color-text-tertiary:  #6B6B70

--color-success:      #2FB768
--color-warning:       #E0A429
--color-danger:        #E5484D
Regla dura: #3b82f6, #2563eb, #1a6bff escrito a mano, #ccc, #111, o cualquier hex fuera de esta lista quedan prohibidos en cualquier archivo del proyecto. Todo color se referencia por variable, siempre.
Regla de uso del dorado: --color-gold no es un color de sistema (no se usa en botones, estados, badges funcionales). Es exclusivamente de identidad: logo, encabezados heroicos puntuales. Mezclarlo con azul como "acento secundario" funcional (como ocurre hoy en detalles sueltos) diluye cuál es el color de acción del producto.
1.2 Estados semánticos — un solo significado por color

Azul (--color-brand) = selección, acción primaria, foco. Nunca se usa para otra cosa.
Verde (--color-success) = confirmación, disponibilidad, éxito.
Ámbar (--color-warning) = advertencia real (ej. "vehículo no catalogado"). No se usa nunca como decoración o para indicar "recomendado" — eso se resuelve con azul.
Rojo (--color-danger) = error de validación o irreversibilidad (cancelar, eliminar).

Ningún color puede tener dos significados en el mismo producto (hoy el ámbar aparece como warning en el Paso 2 del wizard y también sin explicación en los horarios del Paso 3 — mismo color, significados distintos: eso queda eliminado).

2. Tipografía
2.1 Familia única
--font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
login.html deja de usar el stack de sistema operativo y pasa a Montserrat, igual que el resto del producto. La tipografía es la firma más barata y más visible de que "todo es la misma marca" — hoy es el único módulo que rompe esto.
2.2 Escala tipográfica (única para todo el proyecto)
--text-overline:   11px / 600 / +0.08em / uppercase   → labels de sección, "PASO X DE 5"
--text-caption:     13px / 500 / 0                     → labels de campo, texto auxiliar
--text-body:        15px / 400 / 0                     → párrafos, descripciones
--text-body-strong: 15px / 600 / 0                     → valores de datos, ítems de lista
--text-title-sm:    17px / 700 / 0                     → títulos de tarjeta (paquete, servicio)
--text-title-md:    22px / 700 / -0.01em                → títulos de sección (H2 dentro de página)
--text-title-lg:    32px / 900 / -0.02em                → hero, títulos de landing
No existen tamaños intermedios inventados (0.85rem, 0.95rem, 1.1rem sueltos que hoy aparecen en login.html y en distintos puntos de styles.css). Todo tamaño de texto en el proyecto mapea a una de estas 7 categorías.

3. Espaciado
3.1 Escala 4pt estricta
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 24px
--space-6: 32px
--space-7: 48px
--space-8: 64px
Prohibido usar valores en rem sueltos como 0.15rem, 0.38rem, 0.65rem, 0.85rem, 1.1rem, 1.75rem (todos presentes hoy en styles.css). Cualquier padding/margin del proyecto debe resolver a uno de los 8 valores de arriba. Si ninguno "queda bien", el problema es del layout, no del espaciado — se ajusta la estructura, no se inventa un valor nuevo.
3.2 Aplicación estándar

Padding interno de card: --space-4 (16px)
Padding interno de card grande (hero, panel de resumen): --space-5 (24px)
Gap entre elementos de un grupo (chips, botones inline): --space-2 (8px)
Gap entre secciones de una página/paso: --space-5 (24px)
Márgenes laterales de contenedor en mobile: --space-5 (20-24px, fijo en todos los templates)


4. Radios
4.1 Solo 3 valores en todo el proyecto
--radius-sm:   8px    → inputs, chips, badges rectangulares
--radius-md:   14px   → cards, paneles, modales, banners de estado
--radius-full: 999px  → pills, avatares, tabs tipo segmented-control
Elimina: 2px, 3px, 4px, 5px, 6px, 10px, 12px, 16px, 18px, 20px — todos actualmente en uso en algún archivo del proyecto sin criterio. 50% se mantiene solo para elementos circulares reales (avatares, iconos contenedor).

5. Elevación (bordes y sombras)
5.1 Jerarquía de superficies (reemplaza el uso de bordes de 1px como método de diferenciación)
Nivel 0 (fondo):        --color-bg-0, sin sombra
Nivel 1 (card default): --color-bg-1, sin sombra, sin borde
Nivel 2 (card hover/interactiva): --color-bg-1 + box-shadow: 0 2px 8px rgba(0,0,0,0.24)
Nivel 3 (card seleccionada):      --color-bg-2 + box-shadow: 0 0 0 1.5px var(--color-brand), 0 4px 16px var(--color-brand-glow)
Nivel 4 (modal/overlay flotante): --color-bg-1 + box-shadow: 0 12px 32px rgba(0,0,0,0.5)
Regla dura: ningún componente usa border: 1px solid como único diferenciador visual salvo --color-border para separar zonas estáticas (ej. sidebar del admin). Selección, foco y jerarquía se comunican con sombra/tinte, no con líneas.

6. Componentes
6.1 Botones — un solo sistema, tres variantes, en todo el proyecto (público, wizard, admin, auth)
.btn-primary
  background: var(--color-brand)
  color: #fff
  height: 48px
  padding: 0 var(--space-5)
  border-radius: var(--radius-sm)
  font: var(--text-body-strong)
  hover: background var(--color-brand-hover)
  active: scale(0.98)

.btn-secondary
  background: rgba(255,255,255,0.06)   /* nunca borde */
  color: var(--color-text-primary)
  mismas dimensiones que .btn-primary

.btn-danger
  background: var(--color-danger)
  reservado para eliminar/cancelar, uso restringido
Elimina .btn-primary-custom, .btn-outline-custom, .btn-sm-custom, .btn-nav, y cualquier botón propio del wizard — todos migran a estas 3 clases. Un botón "Confirmar Reserva" (compromiso final) puede usar .btn-primary con height: 52px como única excepción documentada de tamaño, no de sistema.
6.2 Inputs — mismo componente en login, wizard, admin y filtros
height: 48px
padding: 0 var(--space-4)
background: var(--color-bg-1)
border: 1px solid var(--color-border)
border-radius: var(--radius-sm)
color: var(--color-text-primary)
placeholder: var(--color-text-tertiary)

:focus → border-color: var(--color-brand) + box-shadow: 0 0 0 3px var(--color-brand-glow)
Hoy login.html define sus propios inputs con padding: 0.75rem 1rem y radio 8px por coincidencia, no por sistema; base_admin.html usa otro padding para .filtros-admin input. Todo input del proyecto —autenticación, wizard, panel admin— se resuelve con esta única especificación.
6.3 Cards de selección (paquetes, tipo de vehículo, servicios)
padding: var(--space-4)
border-radius: var(--radius-md)
background: var(--color-bg-1)
default: sin sombra
hover: Nivel 2
seleccionada: Nivel 3
min-height: 88px, aspect-ratio consistente dentro del mismo grid
6.4 Badges / estados (chips "2 días", "Requiere inspección previa", etc.)
padding: 4px 10px
border-radius: var(--radius-full)
font: var(--text-overline) pero sin uppercase forzado si el texto ya lo es
background tonal según semántica: 
  info    → var(--color-brand-tint) + texto var(--color-brand)
  warning → rgba(224,164,41,0.14) + texto var(--color-warning)
  success → rgba(47,183,104,0.14) + texto var(--color-success)
servicios.html hoy usa badge bg-warning text-dark y badge bg-info text-dark — clases genéricas de Bootstrap con colores que no pertenecen a la paleta del proyecto. Migran a estas variantes tonales.
6.5 Alertas / mensajes flash (login, formularios)
Mismo tratamiento tonal que los badges, pero a nivel de bloque:
padding: var(--space-3) var(--space-4)
border-radius: var(--radius-sm)
sin borde — reemplazar border: 1px solid rgba(...) actual por solo background tonal

7. Iconografía

Un solo set: Font Awesome 6 (ya está disponible en admin y wizard) se convierte en el set oficial único. Se eliminan los SVG custom sueltos del wizard para tipo de vehículo — se reemplazan por equivalentes de Font Awesome o, si no existen, se ilustra un set custom con el mismo stroke-width que el resto (1.5px, nunca mezclado con Font Awesome solid en la misma pantalla).
Contenedor obligatorio: todo ícono funcional (no decorativo) vive dentro de un contenedor de 40×40px, background: rgba(255,255,255,0.05), border-radius: var(--radius-sm). Nunca flota suelto sobre el fondo.
El dorado (--color-gold) nunca tiñe un ícono funcional — queda reservado a marca.


8. Estados de interacción (unificados)
EstadoTratamiento:hover (elemento clickeable)Nivel 2 de elevación, sin cambio de color de texto salvo en links:active (tap/click)transform: scale(0.98), 80ms:focus-visiblebox-shadow: 0 0 0 3px var(--color-brand-glow), nunca outline genérico del navegador salvo como fallback de accesibilidad:disabledopacity: 0.4, cursor: not-allowed, sin cambio de color de fondoseleccionadoNivel 3 de elevación + --color-brand-tint de fondo si aplica

9. Animación (motion tokens)
--duration-fast:   80ms   → feedback táctil (:active, scale)
--duration-base:   200ms  → transiciones de estado (hover, foco, aparición de badge)
--duration-slow:   240ms  → transición entre pasos/pantallas completas

--easing-standard: cubic-bezier(0.25, 0.1, 0.25, 1)   → la mayoría de las transiciones
--easing-pop:      cubic-bezier(0.34, 1.56, 0.64, 1)   → aparición de checks/badges (con overshoot)
Se elimina cualquier transición ad-hoc definida por archivo (hoy styles.css usa 0.2s, 0.25s, 0.3s indistintamente sin relación entre sí). Todo motion del proyecto usa uno de estos tres tiempos.

10. Gobernanza del sistema

Un solo archivo de tokens (tokens.css o equivalente) importado por styles.css, wizard.css y el <style> embebido de base_admin.html. login.html deja de ser standalone: importa el mismo archivo.
Ningún hex, ningún rem suelto, ningún radio fuera de la escala se permite en nuevas reglas CSS — todo pasa por variable.
Cualquier componente nuevo (ej. un badge que no está en esta spec) se diseña primero como extensión del sistema — no como solución puntual del módulo donde nace, que es exactamente cómo se llegó al estado actual (3 sistemas de botones, 2 azules, 11 radios).