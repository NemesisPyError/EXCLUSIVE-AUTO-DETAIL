# Exclusive Auto Detail — Especificación Oficial de Diseño v2
### Manual de Diseño de Producto

> Este documento reemplaza cualquier decisión visual ad-hoc tomada hasta hoy. A partir de aquí, todo lo que se construya en Exclusive Auto Detail —sitio público, wizard de reservas, panel admin, autenticación— se diseña desde este manual, no al revés.

---

# PARTE I — VISIÓN

## 1. El lenguaje visual definitivo

Exclusive Auto Detail no vende un lavado de auto. Vende una experiencia de cuidado meticuloso sobre un objeto que el cliente valora. La interfaz tiene que comunicar esa misma meticulosidad *antes* de que el cliente entregue el vehículo — la app es la primera prueba de calidad del servicio.

El lenguaje visual se apoya en cuatro pilares:

**Oscuridad con propósito, no oscuridad por moda.** El fondo negro no es "dark mode porque se ve moderno" — es el mismo recurso que usa un showroom de autos de lujo: el fondo desaparece para que el producto (el auto, el servicio, el precio) sea lo único que el ojo procesa. Cada elemento que se agrega sobre ese fondo tiene que ganarse su lugar.

**Silencio visual.** La interfaz no grita. No hay gradientes llamativos, no hay múltiples colores de acento compitiendo, no hay texto en mayúscula sostenida gritando urgencia. Hay un azul, usado con disciplina, y un dorado, usado con una disciplina todavía mayor. El lujo discreto se nota en lo que la interfaz decide *no* mostrar.

**Precisión geométrica.** Todo se alinea. Todo respeta una grilla. Todo respeta una escala de espaciado. La sensación de "hecho a mano por alguien que sabe lo que hace" no viene de un detalle espectacular, viene de que nada está torcido, nada tiene un padding que no corresponde, nada rompe el ritmo.

**Materialidad sutil.** Las superficies tienen profundidad —capas de luminosidad, sombras suaves, glow en la selección— pero nunca skeuomorfismo. Es la diferencia entre un iPhone y un dashboard de Windows 95: la profundidad sugiere jerarquía, no textura de plástico.

## 2. Personalidad de la interfaz

Si Exclusive Auto Detail fuera una persona: es el gerente de un detailing shop de autos de alta gama que atiende personalmente a los clientes importantes. Viste bien pero no ostenta. Habla poco pero cada palabra pesa. Nunca te hace esperar sin decirte por qué. Nunca te sorprende con un cargo que no viste venir. Es cálido pero profesional — no es tu amigo, es alguien en quien confiás con tu auto y con tu tarjeta.

La interfaz hereda ese carácter: **confiada, silenciosa, precisa, cálida sin ser efusiva.**

## 3. Qué debe sentir el usuario

- Al abrir la landing: *"esto no es un lavadero de barrio, esto es serio."*
- Al usar el wizard: *"esto sabe exactamente lo que necesita de mí, no me hace pensar."*
- Al llegar al paso de confirmación: *"veo exactamente qué voy a pagar y qué voy a recibir, no hay letra chica."*
- Al tocar cualquier botón: *"esto respondió, se sintió sólido."*
- Al usar el panel admin: *"esta herramienta es rápida, no me hace esperar ni adivinar dónde está cada cosa."*
- Al equivocarse en un formulario: *"me lo dijo de forma clara y amable, no sentí que hice algo mal."*

En ningún momento el usuario debe sentir fricción, sorpresa negativa, o la sensación de estar usando una plantilla genérica.

## 4. Cómo se diferencia de una aplicación Bootstrap

Una interfaz Bootstrap se reconoce por: bordes de 1px definiendo todo, sombras de caja genéricas (`box-shadow: 0 1px 3px rgba(0,0,0,.1)` en todos lados por igual), radios de 4-6px universales, azules saturados de librería, tipografía sin escala deliberada, botones que se ven todos iguales sin importar su importancia, y espaciados que responden al grid de 12 columnas más que a una intención de diseño.

Exclusive Auto Detail se diferencia en:

- **Superficies por luminosidad, no por línea.** Nunca un borde de 1px separa dos superficies del mismo nivel; un salto de brillo lo hace.
- **Sombras con color.** Los elementos seleccionados no tienen sombra gris genérica — tienen un glow tenue del color de marca. Es sutil, pero es el detalle que Bootstrap nunca tiene.
- **Jerarquía real entre acciones.** Un botón de "confirmar y pagar" nunca pesa lo mismo visualmente que un "cancelar" o un "volver". Bootstrap trata a `.btn-primary` y `.btn-secondary` como intercambiables en peso, solo cambia el color.
- **Una escala, no valores sueltos.** Todo espaciado, todo radio, todo tamaño de texto sale de una escala fija. No hay "se ve bien así" — hay "esto es 24px porque 24 está en la escala".
- **Movimiento con intención.** Bootstrap casi no anima nada, o anima con `transition: all .3s` aplicado indiscriminadamente. Acá cada animación tiene una razón y una curva de aceleración propia.
- **Vacíos que respiran, no vacíos que sobran.** El espacio negativo se usa para dar aire a lo importante, nunca como resultado accidental de un layout mal resuelto (como ocurre hoy en el wizard).

## 5. Qué hace que una aplicación se perciba premium

1. **Consistencia obsesiva.** Cada botón del mismo tipo se ve y se comporta exactamente igual en cualquier pantalla del producto.
2. **Feedback físico inmediato.** Todo lo que se toca responde — visualmente y con una leve compresión (`scale`) — en menos de 100ms.
3. **Nunca dejar al usuario sin saber qué está pasando.** Todo estado de carga, error o éxito se comunica de forma clara y con el tono correcto, nunca con silencio ni con un mensaje técnico crudo.
4. **Tipografía tratada como diseño, no como texto.** Tamaños, pesos y espaciados de letra deliberados; nunca "negrita porque sí".
5. **Nada se mueve sin razón, pero lo importante se mueve con gracia.** Confirmar una reserva, marcar un check, abrir un panel — esos momentos merecen una transición cuidada. Un simple hover no necesita coreografía.
6. **El detalle en los extremos.** Cómo se ve un campo vacío, cómo se ve un error, cómo se ve un estado de carga — esos son los momentos donde una interfaz barata se delata. Acá se tratan con el mismo cuidado que la pantalla principal.
7. **Precio y compromiso siempre visibles antes de pedir confirmación.** La transparencia es, en sí misma, un signo de marca premium.

---

# PARTE II — ESPECIFICACIÓN COMPONENTE POR COMPONENTE

## BOTONES

**Altura:** 48px para acciones estándar (Continuar, Guardar, Aplicar filtro). 52px exclusivamente para el botón de compromiso final de un flujo (Confirmar Reserva, Confirmar Pago). 40px para botones secundarios dentro de tablas o filas del admin.

**Sensación:** sólido, denso, nunca fino ni flotante. El texto centrado verticalmente con precisión matemática — un botón mal centrado verticalmente es la señal más rápida de descuido.

**Sombra:** el botón primario no lleva sombra en reposo (vive sobre el fondo con su propio color como diferenciador). Al hacer hover, gana una sombra de color de marca muy tenue hacia abajo — sugiere que "se levanta" ligeramente. El botón secundario nunca lleva sombra, solo cambio tonal de fondo.

**Estados:**
- Reposo: color sólido, sin decoración adicional.
- Hover (desktop): oscurece levemente + sombra tenue de marca.
- Active/pressed: compresión (`scale` leve) + oscurecimiento adicional del 8%, sin sombra — el botón se "hunde".
- Focus (teclado): halo de foco de color de marca, nunca el outline azul genérico del navegador.
- Disabled: opacidad reducida, sin cambio de color base, cursor bloqueado — nunca gris genérico que rompa la paleta.
- Loading: el texto se reemplaza por un spinner minimalista centrado del mismo color que el texto original; el botón mantiene su ancho exacto (nunca "salta" de tamaño al entrar en loading).

**Animación:** transición de color y sombra breve y suave al hover; compresión instantánea y elástica al presionar, liberación con leve rebote al soltar.

**Jerarquía entre variantes:** primario (marca, sólido) > secundario (fondo tonal neutro, sin borde) > terciario/texto (sin fondo, solo color de texto, para acciones de bajo compromiso como "Olvidaste tu contraseña"). Nunca más de un botón primario visible al mismo tiempo en una misma vista.

---

## INPUTS

**Altura:** 48px en todos los formularios del producto (auth, wizard, admin). Ninguna excepción salvo textarea.

**Padding:** interno horizontal generoso, nunca el texto tocando el borde — el aire interno es lo que separa un input premium de uno genérico.

**Placeholder:** siempre en el tono de texto más apagado de la escala, nunca casi invisible (debe seguir siendo legible, es información, no decoración) ni tan oscuro que compita con el valor real ingresado.

**Foco:** el borde cambia a color de marca y aparece un halo suave alrededor de todo el campo — nunca solo un cambio de borde sin halo, el halo es lo que da la sensación de "el campo está vivo ahora".

**Validación en tiempo real:** en campos que lo ameritan (teléfono, email, cédula), el estado de validez se comunica con un ícono discreto a la derecha del campo (check o alerta), nunca cambiando el color del texto que el usuario está escribiendo — el valor que el usuario ve mientras tipea siempre es el mismo color neutro, sin excepción.

**Estado de error:** borde y halo cambian a tono de alerta, y aparece un mensaje breve debajo del campo, con un ícono pequeño que acompaña el texto — nunca solo texto rojo suelto sin jerarquía.

**Estado de éxito:** un check discreto aparece a la derecha del campo con una transición suave de aparición — nunca cambia el fondo del input a verde (eso se siente infantil, no premium).

**Label:** siempre visible arriba del campo (nunca floating label que desaparece — en un producto que prioriza claridad, el usuario nunca debe dudar qué campo está llenando).

---

## CARDS

**Estructura:** un padding interno uniforme, contenido organizado en un eje vertical claro (ícono opcional arriba, título, descripción, metadato), nunca elementos flotando sin relación de espaciado entre sí.

**Ritmo interno:** salto claro y consistente entre el título y la descripción; salto mayor entre el bloque de contenido y cualquier badge o etiqueta adicional (como "2 días"). El ritmo interno de una card debe sentirse igual sin importar en qué paso del producto aparezca.

**Jerarquía:** el título siempre es el elemento más pesado visualmente dentro de la card; la descripción es secundaria y nunca compite en peso; cualquier metadato (precio, duración, tag) tiene su propio tratamiento visual distintivo, nunca mezclado tipográficamente con el título.

**Selección:** una card seleccionada se distingue por cambio de superficie (más luminosa) + glow de color de marca alrededor, nunca solo por un borde de color. El cambio debe ser evidente incluso vista de reojo, sin tener que leer el contenido.

**Hover (donde aplique, principalmente admin/desktop):** leve elevación con sombra suave, sin cambio de color de fondo — sugiere "esto es tocable" sin adelantar el estado de selección.

**Active/tap:** compresión leve al presionar, igual que los botones — todo elemento tocable del sistema comparte este mismo lenguaje de respuesta física.

---

## BADGES

Pequeños, de una sola línea, nunca truncados. Fondo tonal (nunca sólido saturado) del color semántico correspondiente, texto del mismo color en versión más intensa. Forma de píldora. Se usan para comunicar un solo dato (estado, categoría, duración) — nunca se combinan dos datos en un mismo badge.

---

## CHIPS

Usados para selección múltiple o única dentro de un grupo (adicionales, niveles de suciedad, horarios). Reposo: fondo tonal neutro apenas perceptible sobre el fondo de card. Seleccionado: fondo tonal de marca + texto en color de marca, sin necesidad de check adicional salvo que el contexto lo requiera (ej. selección múltiple, donde un check discreto ayuda a escanear rápido cuántos están activos). Todos los chips de un mismo grupo comparten exactamente la misma altura, sin importar el largo del texto — el texto se ajusta, el chip no se deforma.

---

## ACCORDIONS

Usados para categorías de servicios. El header del accordion siempre tiene el mismo peso tipográfico que los demás headers de sección del sistema (nunca un tamaño inventado para "que se note que es clickeable" — el ícono de expandir/colapsar ya comunica eso). La expansión y colapso se anima con una transición de altura suave, nunca un salto abrupto. El ícono de flecha rota con la misma curva de animación que el resto del sistema, nunca instantáneo.

---

## BOTTOM SHEET

Usado en mobile para el resumen de reserva ("Ver resumen"). Aparece desde abajo con una curva de desaceleración marcada — entra rápido, frena suave, nunca rebota exageradamente. Tiene un grabber (indicador de arrastre) sutil, delgado, con esquinas redondeadas y opacidad reducida — es un affordance, no un elemento decorativo que compita por atención. El fondo detrás del sheet se oscurece levemente para dar foco, con una transición de opacidad simultánea a la aparición del sheet, nunca después.

---

## SIDEBAR (admin)

Fondo apenas diferenciado del contenido principal (una capa de luminosidad, nunca un color completamente distinto). El ítem activo se distingue por fondo tonal de marca + texto en color de marca, nunca solo negrita. Los íconos de navegación comparten exactamente el mismo peso de trazo que el resto de la iconografía del sistema. Transición de hover suave, sin saltos.

---

## STEPPER (wizard, "Paso X de 5")

La barra de progreso nunca es un elemento decorativo aislado — comunica con precisión cuánto falta. Relleno con transición suave de ancho al avanzar (nunca instantáneo, nunca tan lento que se sienta pesado). El número de paso actual se comunica con el mismo tratamiento tipográfico en las 5 pantallas, sin variación. Retroceder anima la barra hacia atrás con la misma curva, nunca un salto brusco que se sienta como error.

---

## MODALES

Reservados para decisiones que requieren atención total (confirmar eliminación, cambios irreversibles). Aparecen con una leve escala de entrada (de 96% a 100%) combinada con fade, nunca solo fade seco ni un slide brusco. El fondo se oscurece con blur sutil, no solo opacidad plana — el blur es lo que distingue un modal premium de uno genérico. Nunca se cierran solos ni con temporizador — el usuario decide cuándo salir, salvo confirmaciones de éxito no críticas.

---

## TABLAS (admin)

Filas con separación por diferencia de superficie cada segunda fila (zebra sutil, casi imperceptible) en vez de líneas divisorias duras. Header de tabla con tratamiento tipográfico de overline (pequeño, con tracking), nunca del mismo tamaño que el contenido de las celdas. Hover de fila con cambio de superficie leve, nunca un color que distraiga. Las acciones por fila (editar, eliminar, cambiar estado) aparecen con peso visual bajo por defecto y solo ganan protagonismo al hacer hover sobre la fila — reduce el ruido visual cuando se está simplemente escaneando la tabla.

---

## FORMULARIOS

Agrupados por bloques lógicos con separación clara entre bloques (nunca todos los campos como una lista continua sin respiro). Orden de tabulación siempre predecible de arriba hacia abajo, izquierda a derecha. Los campos obligatorios se marcan con un tratamiento discreto y consistente (nunca asteriscos rojos agresivos — un asterisco del mismo color que el label es suficiente). El botón de envío del formulario siempre es el elemento con más peso visual de toda la pantalla.

---

## RESUMEN (sidebar / paso final del wizard)

Estructura de lista con label a la izquierda (tratamiento de overline) y valor a la derecha (tratamiento de dato fuerte), separados por una línea divisoria sutil entre filas. El precio total, si aparece, se distingue del resto de las filas con mayor tamaño y peso — es el dato más importante de toda la pantalla y debe leerse antes que cualquier otro elemento. Cada fila del resumen es tocable para editar, y esa capacidad se comunica con un tratamiento visual muy sutil (nunca un lápiz genérico gigante) — un leve cambio de superficie al hover en desktop, o simplemente el affordance implícito en mobile de que toda la fila responde al tap.

---

## TOASTS

Aparecen desde arriba o desde abajo (nunca desde el costado en mobile), con una entrada rápida y una salida ligeramente más lenta —entran con urgencia, se van con calma—. Nunca se apilan más de dos a la vez; si hay un tercero pendiente, reemplaza al más antiguo con una transición de cruce suave, nunca un salto. Duración en pantalla suficiente para leer el mensaje completo sin apuro, con una barra de progreso opcional muy sutil si el diseño lo permite.

---

## MENSAJES / ALERTAS (flash messages de login, avisos de formulario)

Tratamiento tonal (fondo tenue del color semántico + texto en la versión intensa del mismo color), nunca fondo sólido saturado ni borde grueso. Íconos pequeños y consistentes acompañando cada tipo de mensaje. Aparecen con una transición de entrada suave (fade + leve desplazamiento vertical), nunca aparición instantánea que sobresalte.

---

## LOADING

Nunca un spinner genérico de librería. El sistema usa **skeletons** (siluetas de contenido con un shimmer sutil) para cargas de contenido estructurado (listas, cards, tablas) — comunica "esto va a tener esta forma" en vez de solo "esperá". Para acciones puntuales (botón enviando, guardando), un spinner minimalista de trazo fino del color correspondiente al contexto. Nunca se bloquea toda la pantalla con un overlay de carga salvo en transiciones de página completas — dentro de un flujo, el loading siempre es local al componente que está cargando.

---

## EMPTY STATES

Nunca solo texto gris centrado ("No hay servicios disponibles" tal como aparece hoy). Un empty state premium tiene: una ilustración o ícono simple y de línea consistente con el sistema, un mensaje principal breve y humano (no técnico), y —cuando aplica— una acción clara para resolver el vacío. El tono nunca es de error, es informativo y tranquilo.

---

## ERROR STATES

Mismo principio que los empty states pero con un matiz de urgencia moderada: ícono de alerta discreto, mensaje claro sobre qué pasó (en lenguaje humano, nunca un código o traza técnica), y una acción de recuperación siempre visible ("Reintentar", "Volver"). Nunca se le muestra al usuario un mensaje que no pueda accionar de alguna forma.

---

## PÁGINA DE CONFIRMACIÓN (post-reserva)

Es un momento de cierre emocional del flujo — merece más aire y más calma que cualquier otra pantalla del wizard. Un ícono o marca de éxito centrado con una animación de entrada suave y celebratoria pero contenida (nunca confetti ni efectos excesivos — el lujo discreto también aplica a los momentos de éxito). El resumen de la reserva confirmada se presenta con el mismo tratamiento visual que el resumen del paso 5, para dar continuidad. Una acción clara de siguiente paso (agregar a calendario, volver al inicio) sin saturar la pantalla de opciones.

---

## LOGIN

Deja de sentirse como una pantalla aislada del resto del producto. Comparte exactamente la misma tipografía, radios, espaciados y tratamiento de inputs/botones que el wizard y el admin. La marca (logo + nombre) tiene protagonismo centrado y calmo, sin la urgencia de "convertir" que sí tiene la landing — es una puerta de entrada para alguien que ya sabe a dónde va. El fondo puede tener una sutileza adicional (un gradiente radial extremadamente tenue detrás de la card) para diferenciarse levemente de una pantalla de formulario plana, sin romper la paleta.

---

## LANDING

Es la única superficie del producto donde se permite algo más de dinamismo visual (fotografía de autos, testimonios, sensación editorial) — pero siempre dentro de la misma paleta y tipografía del sistema. La jerarquía debe guiar al usuario hacia una sola acción principal ("Reservar Turno"), presente y visualmente dominante en cada sección relevante, nunca compitiendo con múltiples CTAs del mismo peso. Las imágenes de autos y trabajos realizados deben tratarse con el mismo cuidado que una vidriera de showroom: buena luz, buen recorte, consistencia de proporción entre todas las fotos de una misma grilla.

---

## PANEL ADMIN

Prioriza densidad de información sobre estética decorativa — es una herramienta de trabajo diario, no una vidriera. Pero "denso" no significa "descuidado": mismos tokens de color, tipografía y espaciado que el resto del producto, simplemente con una escala de espaciado más compacta permitida específicamente para tablas y listas de gestión. Cada acción destructiva (eliminar, cancelar) requiere siempre una confirmación explícita con el mismo lenguaje de modal definido arriba, nunca una eliminación de un solo tap.

---

# PARTE III — MOTION SYSTEM

## Principio rector
El movimiento comunica relación de causa y efecto, jerarquía y continuidad espacial. Si una animación no cumple una de esas tres funciones, no existe.

## Duraciones
```
Instantáneo (feedback táctil):        80–100ms
Transición de estado (hover, foco):   150–200ms
Transición de componente (abrir/cerrar acordeón, aparecer badge): 200–240ms
Transición de pantalla completa (paso a paso del wizard): 220–260ms
Celebración (confirmación de éxito):  400–600ms, una sola vez, nunca en loop
```

## Curvas de aceleración
- **Estándar (la mayoría de las transiciones):** desaceleración suave, entra con algo de velocidad y frena con calma. Es la curva por defecto de todo el sistema.
- **Salida (elementos que se van, cierres):** aceleración suave, arranca despacio y sale con más velocidad — un elemento que se despide no debe demorar la atención del usuario.
- **Entrada con rebote leve (checks, badges, confirmaciones):** ligero overshoot antes de asentarse — es lo que da la sensación "táctil" de que algo apareció con intención, no que simplemente se renderizó.

## Cuándo animar
- Cambios de selección (chip, card, radio, checkbox).
- Apariciones y desapariciones de contenido condicional (banners, mensajes de validación, badges).
- Transiciones entre pasos de un flujo.
- Apertura/cierre de bottom sheets, modales, acordeones.
- Feedback de presión en cualquier elemento tocable.
- Momentos de éxito o cierre de un flujo importante.
- Cambios de valor numérico relevantes (precio actualizándose) — transición de crossfade o conteo suave, nunca un salto de número seco.

## Cuándo NO animar
- Contenido que aparece al cargar la página por primera vez arriba del fold (debe estar ahí de inmediato, no "aparecer").
- Texto dentro de inputs mientras el usuario escribe.
- Elementos que cambian de tamaño por contenido dinámico impredecible (evitar animar reflows de layout que puedan verse entrecortados).
- Cualquier animación en loop indefinido sin propósito (spinners decorativos donde no hay carga real, íconos que "laten" sin razón).
- Nunca más de una animación de entrada compitiendo por atención al mismo tiempo en la misma vista.

---

# PARTE IV — Pequeños detalles que hacen que una aplicación se sienta de nivel Apple

- **Un check no aparece, se asienta.** Escala desde un punto pequeño hasta su tamaño final con un leve rebote, nunca un fade plano ni un pop instantáneo.
- **Un panel no se cierra, se retira.** Sale con un desplazamiento y fade combinados, en la dirección de donde vino — un bottom sheet baja al cerrarse, nunca desaparece en el lugar.
- **Un botón no cambia, respira.** Al pasar de estado reposo a loading, el ancho se mantiene exactamente igual — nada "salta" de tamaño.
- **Una card no reacciona, se comprime levemente al tocarla** — como si tuviera un mínimo de profundidad física, y vuelve a su forma al soltar.
- **Un badge no se actualiza, se reemplaza con una transición de cruce** — el número o texto viejo se desvanece mientras el nuevo aparece, nunca un cambio abrupto de contenido.
- **Un input válido no grita su validez** — el check de confirmación aparece pequeño, silencioso, a la derecha, sin cambiar el carácter del campo.
- **Una transición de pantalla se siente como continuidad, no como corte** — el contenido saliente y el entrante nunca se cruzan en el mismo punto exacto de la pantalla sin una relación de dirección clara.
- **El cursor de foco de teclado nunca desaparece de forma abrupta** — se desvanece con la misma suavidad con la que apareció.
- **Los números de precio no saltan, cuentan** — cuando el precio se recalcula (por ejemplo al sumar un adicional), el cambio se anima brevemente en vez de reemplazarse de golpe.
- **El scroll nunca se siente "pegajoso"** — cualquier elemento sticky (footer de navegación, header) tiene una transición de sombra/blur sutil que aparece solo cuando hay contenido detrás, nunca una sombra fija todo el tiempo.
- **Los mensajes de error nunca "empujan" el layout de forma brusca** — el espacio para el mensaje de error se reserva con una transición de altura suave, no un salto que mueve todo lo que está debajo.
- **Todo elemento interactivo tiene un área de toque generosa aunque visualmente sea pequeño** — el usuario nunca "falla" un tap por un ícono demasiado ajustado a su contenido visual.

---

# PARTE V — Implementación por Fases (para OpenCode)

## FASE 1 — Tokens
**Qué incluye:** definición única y centralizada de color, tipografía, espaciado, radios, sombras y motion tokens descritos en este documento y en el Design System v1.
**Prioridad:** Máxima — todo lo demás depende de esto.
**Impacto visual:** Bajo de forma directa (no se ve un cambio en pantalla todavía), pero es la base de todo impacto futuro.
**Dificultad:** Baja.
**Riesgo:** Bajo, siempre que se audite que ningún archivo existente siga con valores hardcodeados en paralelo.
**Dependencias:** Ninguna — es el punto de partida.

## FASE 2 — Componentes base
**Qué incluye:** botones, inputs, cards, badges, chips, alertas, toasts, modales, loading states, empty states — como piezas reutilizables independientes de cualquier pantalla específica.
**Prioridad:** Muy alta.
**Impacto visual:** Alto — es donde el producto empieza a "sentirse" distinto por primera vez.
**Dificultad:** Media.
**Riesgo:** Medio — si estos componentes no quedan bien resueltos, el problema se replica en cada pantalla que los use después.
**Dependencias:** Fase 1 completa.

## FASE 3 — Login y Landing
**Qué incluye:** unificación de `login.html` al sistema de tokens y componentes; ajuste de la landing pública a la tipografía, espaciado y componentes definidos, sin alterar su estructura de contenido.
**Prioridad:** Alta (son la primera impresión del producto).
**Impacto visual:** Alto.
**Dificultad:** Baja–Media.
**Riesgo:** Bajo — son superficies relativamente aisladas y de bajo riesgo funcional.
**Dependencias:** Fase 1 y 2.

## FASE 4 — Wizard de reservas
**Qué incluye:** stepper, cards de selección, chips, bottom sheet de resumen, formularios, pantalla de confirmación, página de éxito post-reserva.
**Prioridad:** Muy alta (es el corazón transaccional del producto).
**Impacto visual:** Muy alto.
**Dificultad:** Alta — es el flujo más complejo y con más estados distintos del producto.
**Riesgo:** Medio-alto — al ser el flujo que genera ingresos, cualquier cambio debe validarse con cuidado antes de reemplazar el actual.
**Dependencias:** Fase 1, 2 y 3 completas (reutiliza inputs, botones y cards ya resueltos ahí).

## FASE 5 — Panel Admin
**Qué incluye:** sidebar, tablas, filtros, formularios de edición, modales de confirmación, badges de estado.
**Prioridad:** Media-alta (impacto directo en la eficiencia operativa diaria, menor impacto en la percepción de marca del cliente final).
**Impacto visual:** Medio (prioriza densidad funcional sobre expresión visual).
**Dificultad:** Media.
**Riesgo:** Medio — es una herramienta de uso diario del equipo, cualquier fricción nueva introducida afecta el trabajo real, no solo la estética.
**Dependencias:** Fase 1 y 2 completas.

## FASE 6 — Pulido (Motion + detalles finos)
**Qué incluye:** implementación completa del motion system, los "pequeños detalles nivel Apple" descritos en la Parte IV, revisión de estados de foco/accesibilidad, ajuste fino de sombras y glows en todos los componentes ya migrados.
**Prioridad:** Alta, pero solo tiene sentido después de que el resto exista — es la capa que convierte "correcto" en "premium".
**Impacto visual:** Muy alto en percepción, aunque cada cambio individual sea pequeño.
**Dificultad:** Media-alta (requiere revisión componente por componente, no es un cambio global de una sola vez).
**Riesgo:** Bajo — son ajustes no destructivos sobre una base ya funcional.
**Dependencias:** Fases 1 a 5 completas.

---

*Este documento es la especificación oficial de diseño de Exclusive Auto Detail. Cualquier decisión visual futura debe verificarse contra este manual antes de implementarse. Si una necesidad nueva no está contemplada aquí, se extiende el sistema formalmente — nunca se resuelve de forma puntual dentro de una sola pantalla.*