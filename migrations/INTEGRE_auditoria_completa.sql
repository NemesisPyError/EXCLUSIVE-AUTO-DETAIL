-- ============================================================================
-- INFORME: AUDITORIA COMPLETA DE INTEGRIDAD - PostgreSQL
-- Fecha: 2026-07-09
-- Base: exclusive_autodetail
-- ============================================================================

-- ============================================================================
-- HALLAZGOS CLASIFICADOS POR SEVERIDAD
-- ============================================================================

-- ============================================================================
-- CRITICO
-- ============================================================================
-- No se encontraron problemas criticos que impidan el funcionamiento del
-- sistema de reservas.
-- ============================================================================


-- ============================================================================
-- ALTO
-- ============================================================================

-- [ALTO-01] Tipos_box Acuatico (14) y Exterior (15) sin boxes fisicos
-- Jet Ski y Lancha/Bote dependen de estas para tener boxes disponibles.
-- Resultado: reservas para estos tipos de vehiculo fallaran con HTTP 409
-- (no hay box compatible) porque Estandar/Grande/Moto no los aceptan.
-- Correccion sugerida: Crear al menos 1 box fisico para cada tipo_box.
-- (Requiere decision de negocio sobre cantidades y capacidad)
SELECT
  'ALTO' as severidad,
  'ALTO-01' as codigo,
  'Tipos_box sin boxes fisicos' as hallazgo,
  tb.nombre as detalle,
  tb.descripcion
FROM tipos_box tb
WHERE NOT EXISTS (SELECT 1 FROM boxes b WHERE b.tipo_box_id = tb.id AND b.activo = true)
ORDER BY tb.id;

-- [ALTO-02] Todos los modelos_vehiculo clasificados como Auto+Mediano
-- 57 de 57 modelos tienen tipo_vehiculo_id=22 (Auto) y segmento_id=10
-- (Mediano). Esto genera problemas en el wizard: al seleccionar un
-- modelo, se asigna tipo=Auto+Mediano siempre, forzando al usuario a
-- corregir manualmente si el vehiculo real es SUV, pickup, etc.
-- Vehiculos afectados (ejemplos):
--   SUV: RAV4, Sportage, CR-V, Tucson, Santa Fe, Sorento, Fortuner
--   Pickup: Hilux, Amarok, Ranger, S10, Frontier, Strada, Toro
--   Van: Hiace, Carnival, Spin
-- Correccion sugerida: Actualizar tipo_vehiculo_id y segmento_id de
-- cada modelo segun su clasificacion real.
-- (Requiere regla de negocio: que tipo/segmento tiene cada modelo)
SELECT
  'ALTO' as severidad,
  'ALTO-02' as codigo,
  'Modelos clasificados incorrectamente' as hallazgo,
  mv.nombre as modelo_clasificado_como_auto_mediano,
  tv.nombre as tipo_actual,
  seg.nombre as segmento_actual
FROM modelos_vehiculo mv
JOIN tipos_vehiculo tv ON tv.id = mv.tipo_vehiculo_id
JOIN segmentos seg ON seg.id = mv.segmento_id
WHERE tv.slug = 'auto' AND seg.slug = 'mediano'
  AND mv.nombre IN ('RAV4','Sportage','CR-V','HR-V','Tucson','Santa Fe',
                     'Fortuner','Land Cruiser','Sorento','Bronco','Duster','Kicks',
                     'Hilux','Amarok','Ranger','S10','Frontier','Strada','Toro','Oroch',
                     'Hiace','Carnival','Spin')
ORDER BY mv.nombre;


-- ============================================================================
-- MEDIO
-- ============================================================================

-- [MEDIO-01] Sin domingo en horarios (dia_semana=0 ausente)
-- El seed solo configura Lunes-Sabado (1-6). Domingo (0) no tiene
-- horarios. Esto es coherente con el seed pero impide reservas los
-- domingos. Verificar si es intencional.
SELECT
  'MEDIO' as severidad,
  'MEDIO-01' as codigo,
  'Sin horarios para domingo' as hallazgo,
  'dia_semana=0 ausente de la tabla horarios' as detalle
WHERE NOT EXISTS (SELECT 1 FROM horarios h WHERE h.dia_semana = 0);

-- [MEDIO-02] Tabla configuracion vacia
-- La tabla existe pero no tiene registros. Si el sistema depende de
-- configuraciones (horarios especiales, precios globales, etc.), no
-- las encontrara.
SELECT
  'MEDIO' as severidad,
  'MEDIO-02' as codigo,
  'Tabla configuracion vacia' as hallazgo,
  COUNT(*)::text || ' registros' as detalle
FROM configuracion;

-- [MEDIO-03] Tipos_box Exterior (15) mapeado a 10 tipos de vehiculo
-- pero sin boxes fisicos. El mapeo box_tipo_vehiculo incluye Exterior
-- para todos los tipos. Si se crea un box Exterior, todos tendran
-- disponibilidad ahi, pero ninguno tiene uno real.
SELECT
  'MEDIO' as severidad,
  'MEDIO-03' as codigo,
  'Exterior mapeado a todos los tipos pero sin boxes' as hallazgo,
  COUNT(DISTINCT btv.tipo_vehiculo_id)::text || ' tipos afectados' as detalle
FROM box_tipo_vehiculo btv
WHERE btv.tipo_box_id = 15;


-- ============================================================================
-- BAJO
-- ============================================================================

-- [BAJO-01] Solo 1 usuario admin registrado
-- Un solo admin puede ser un cuello de botella. Verificar si se
-- requieren mas usuarios para operacion diaria.
SELECT
  'BAJO' as severidad,
  'BAJO-01' as codigo,
  'Un solo usuario registrado (admin)' as hallazgo,
  u.email as detalle
FROM usuarios u;

-- [BAJO-02] Reserva 1 con precio_final_base NULL
-- La reserva existe pero precio_final_base no tiene valor. Esto puede
-- indicar una reserva incompleta o un problema en el flujo de creacion.
SELECT
  'BAJO' as severidad,
  'BAJO-02' as codigo,
  'Reserva con precio_final_base NULL' as hallazgo,
  r.id || ' - servicio_id=' || r.servicio_id || ' - precio_estimado=' || r.precio_estimado_base as detalle
FROM reservas r
WHERE r.precio_final_base IS NULL;

-- [BAJO-03] Sin testimonios registrados
-- La tabla testimonios existe pero esta vacia. Verificar si es
-- funcional o solo estructura预留.
SELECT
  'BAJO' as severidad,
  'BAJO-03' as codigo,
  'Tabla testimonios vacia' as hallazgo,
  COUNT(*)::text || ' registros' as detalle
FROM testimonios;

-- [BAJO-04] Sin estados_cambio registrados
-- Tabla vacia. Verificar si es funcional o solo estructura预留.
SELECT
  'BAJO' as severidad,
  'BAJO-04' as codigo,
  'Tabla estados_cambio vacia' as hallazgo,
  COUNT(*)::text || ' registros' as detalle
FROM estados_cambio;

-- [BAJO-05] Sin solicitudes_catalogo registradas
SELECT
  'BAJO' as severidad,
  'BAJO-05' as codigo,
  'Tabla solicitudes_catalogo vacia' as hallazgo,
  COUNT(*)::text || ' registros' as detalle
FROM solicitudes_catalogo;

-- [BAJO-06] Sin fotografias_reserva registradas
SELECT
  'BAJO' as severidad,
  'BAJO-06' as codigo,
  'Tabla fotografias_reserva vacia' as hallazgo,
  COUNT(*)::text || ' registros' as detalle
FROM fotografias_reserva;

-- [BAJO-07] Sin galeria categorias definida (solo 6 registros pre-cargados)
-- La galeria tiene 6 fotos pero solo categorias basicas. Verificar si
-- es suficiente para el frontend.
SELECT
  'BAJO' as severidad,
  'BAJO-07' as codigo,
  'Galeria con pocas categorias' as hallazgo,
  COUNT(DISTINCT gc.id)::text || ' categorias, ' || COUNT(DISTINCT g.id)::text || ' fotos' as detalle
FROM galeria_categorias gc
LEFT JOIN galeria g ON g.categoria_id = gc.id;


-- ============================================================================
-- VERIFICACIONES ADICIONALES
-- ============================================================================

-- [VERIF-01] Secuencias PostgreSQL: alineacion
-- Verificar que las secuencias estan por encima del maximo ID de cada tabla
-- para evitar conflictos de claves primarias futuras.
SELECT
  pg_sequences.sequencename as secuencia,
  pg_sequences.last_value as ultimo_valor_secuencia,
  max_ids.tabla,
  max_ids.max_id,
  CASE 
    WHEN pg_sequences.last_value IS NULL THEN 'SIN VALOR (vacia)'
    WHEN pg_sequences.last_value >= max_ids.max_id THEN 'ALINEADO'
    ELSE 'DESALINEADO - RIESGO DE CONFLICTO'
  END as estado
FROM pg_sequences
LEFT JOIN LATERAL (
  SELECT 'reservas' as tabla, MAX(id) as max_id FROM reservas
  UNION ALL SELECT 'clientes', MAX(id) FROM clientes
  UNION ALL SELECT 'vehiculos', MAX(id) FROM vehiculos
  UNION ALL SELECT 'servicios', MAX(id) FROM servicios
  UNION ALL SELECT 'usuarios', MAX(id) FROM usuarios
  UNION ALL SELECT 'boxes', MAX(id) FROM boxes
  UNION ALL SELECT 'tipos_vehiculo', MAX(id) FROM tipos_vehiculo
  UNION ALL SELECT 'tipos_box', MAX(id) FROM tipos_box
  UNION ALL SELECT 'segmentos', MAX(id) FROM segmentos
  UNION ALL SELECT 'niveles_suciedad', MAX(id) FROM niveles_suciedad
  UNION ALL SELECT 'marcas', MAX(id) FROM marcas
  UNION ALL SELECT 'modelos_vehiculo', MAX(id) FROM modelos_vehiculo
  UNION ALL SELECT 'horarios', MAX(id) FROM horarios
  UNION ALL SELECT 'categorias_servicio', MAX(id) FROM categorias_servicio
  UNION ALL SELECT 'galeria_categorias', MAX(id) FROM galeria_categorias
  UNION ALL SELECT 'galeria', MAX(id) FROM galeria
  UNION ALL SELECT 'estados_reserva', MAX(id) FROM estados_reserva
  UNION ALL SELECT 'precios_servicio', MAX(id) FROM precios_servicio
) max_ids ON max_ids.tabla = REPLACE(pg_sequences.sequencename, '_id_seq', '')
WHERE pg_sequences.schemaname = 'public'
ORDER BY pg_sequences.sequencename;

-- [VERIF-02] Claves foraneas: registros huerfanos (TODAS las tablas)
SELECT
  'reservas->cliente' as fk, COUNT(*) as huerfanos FROM reservas r LEFT JOIN clientes c ON c.id = r.cliente_id WHERE c.id IS NULL AND r.cliente_id IS NOT NULL
UNION ALL SELECT 'reservas->vehiculo', COUNT(*) FROM reservas r LEFT JOIN vehiculos v ON v.id = r.vehiculo_id WHERE v.id IS NULL AND r.vehiculo_id IS NOT NULL
UNION ALL SELECT 'reservas->servicio', COUNT(*) FROM reservas r LEFT JOIN servicios s ON s.id = r.servicio_id WHERE s.id IS NULL AND r.servicio_id IS NOT NULL
UNION ALL SELECT 'reservas->estado', COUNT(*) FROM reservas r LEFT JOIN estados_reserva er ON er.id = r.estado_reserva_id WHERE er.id IS NULL AND r.estado_reserva_id IS NOT NULL
UNION ALL SELECT 'reservas->suciedad', COUNT(*) FROM reservas r LEFT JOIN niveles_suciedad ns ON ns.id = r.nivel_suciedad_id WHERE ns.id IS NULL AND r.nivel_suciedad_id IS NOT NULL
UNION ALL SELECT 'reservas->box', COUNT(*) FROM reservas r LEFT JOIN boxes b ON b.id = r.box_id WHERE b.id IS NULL AND r.box_id IS NOT NULL
UNION ALL SELECT 'reservas->usuario_asignado', COUNT(*) FROM reservas r LEFT JOIN usuarios u ON u.id = r.usuario_asignado_id WHERE u.id IS NULL AND r.usuario_asignado_id IS NOT NULL
UNION ALL SELECT 'vehiculos->cliente', COUNT(*) FROM vehiculos vh LEFT JOIN clientes c ON c.id = vh.cliente_id WHERE c.id IS NULL AND vh.cliente_id IS NOT NULL
UNION ALL SELECT 'vehiculos->tipo', COUNT(*) FROM vehiculos vh LEFT JOIN tipos_vehiculo tv ON tv.id = vh.tipo_vehiculo_id WHERE tv.id IS NULL AND vh.tipo_vehiculo_id IS NOT NULL
UNION ALL SELECT 'vehiculos->marca', COUNT(*) FROM vehiculos vh LEFT JOIN marcas m ON m.id = vh.marca_id WHERE m.id IS NULL AND vh.marca_id IS NOT NULL
UNION ALL SELECT 'vehiculos->modelo', COUNT(*) FROM vehiculos vh LEFT JOIN modelos_vehiculo mv ON mv.id = vh.modelo_id WHERE mv.id IS NULL AND vh.modelo_id IS NOT NULL
UNION ALL SELECT 'vehiculos->segmento', COUNT(*) FROM vehiculos vh LEFT JOIN segmentos seg ON seg.id = vh.segmento_id WHERE seg.id IS NULL AND vh.segmento_id IS NOT NULL
UNION ALL SELECT 'reserva_adicionales->reserva', COUNT(*) FROM reserva_adicionales ra LEFT JOIN reservas r ON r.id = ra.reserva_id WHERE r.id IS NULL AND ra.reserva_id IS NOT NULL
UNION ALL SELECT 'reserva_adicionales->servicio', COUNT(*) FROM reserva_adicionales ra LEFT JOIN servicios s ON s.id = ra.servicio_id WHERE s.id IS NULL AND ra.servicio_id IS NOT NULL
UNION ALL SELECT 'precios->servicio', COUNT(*) FROM precios_servicio ps LEFT JOIN servicios s ON s.id = ps.servicio_id WHERE s.id IS NULL
UNION ALL SELECT 'precios->tipo_veh', COUNT(*) FROM precios_servicio ps LEFT JOIN tipos_vehiculo tv ON tv.id = ps.tipo_vehiculo_id WHERE tv.id IS NULL
UNION ALL SELECT 'precios->segmento', COUNT(*) FROM precios_servicio ps LEFT JOIN segmentos seg ON seg.id = ps.segmento_id WHERE seg.id IS NULL
UNION ALL SELECT 'precios->suciedad', COUNT(*) FROM precios_servicio ps LEFT JOIN niveles_suciedad ns ON ns.id = ps.nivel_suciedad_id WHERE ns.id IS NULL
UNION ALL SELECT 'servicio_tipo_veh->servicio', COUNT(*) FROM servicio_tipo_vehiculo stv LEFT JOIN servicios s ON s.id = stv.servicio_id WHERE s.id IS NULL
UNION ALL SELECT 'servicio_tipo_veh->tipo_veh', COUNT(*) FROM servicio_tipo_vehiculo stv LEFT JOIN tipos_vehiculo tv ON tv.id = stv.tipo_vehiculo_id WHERE tv.id IS NULL
UNION ALL SELECT 'box_tipo_veh->tipo_box', COUNT(*) FROM box_tipo_vehiculo btv LEFT JOIN tipos_box tb ON tb.id = btv.tipo_box_id WHERE tb.id IS NULL
UNION ALL SELECT 'box_tipo_veh->tipo_veh', COUNT(*) FROM box_tipo_vehiculo btv LEFT JOIN tipos_vehiculo tv ON tv.id = btv.tipo_vehiculo_id WHERE tv.id IS NULL
UNION ALL SELECT 'galeria->categoria', COUNT(*) FROM galeria g LEFT JOIN galeria_categorias gc ON gc.id = g.categoria_id WHERE gc.id IS NULL AND g.categoria_id IS NOT NULL
UNION ALL SELECT 'servicios->categoria', COUNT(*) FROM servicios s LEFT JOIN categorias_servicio cs ON cs.id = s.categoria_servicio_id WHERE cs.id IS NULL AND s.categoria_servicio_id IS NOT NULL;

-- [VERIF-03] Duplicados en tablas con slugs unicos
SELECT 'servicios' as tabla, slug as valor, COUNT(*) as duplicados
FROM servicios WHERE deleted_at IS NULL GROUP BY slug HAVING COUNT(*) > 1
UNION ALL
SELECT 'tipos_vehiculo', slug, COUNT(*) FROM tipos_vehiculo GROUP BY slug HAVING COUNT(*) > 1
UNION ALL
SELECT 'segmentos', slug, COUNT(*) FROM segmentos GROUP BY slug HAVING COUNT(*) > 1
UNION ALL
SELECT 'categorias_servicio', slug, COUNT(*) FROM categorias_servicio GROUP BY slug HAVING COUNT(*) > 1
UNION ALL
SELECT 'modelos_vehiculo', nombre, COUNT(*) FROM modelos_vehiculo GROUP BY nombre HAVING COUNT(*) > 1;

-- [VERIF-04] Servicios activos sin categoria_servicio_id
SELECT s.id, s.nombre, s.tipo
FROM servicios s
WHERE s.categoria_servicio_id IS NULL AND s.deleted_at IS NULL;


-- ============================================================================
-- RESUMEN EJECUTIVO
-- ============================================================================
-- CRITICO: 0 problemas
-- ALTO:    2 problemas (boxes sin fisicos, modelos mal clasificados)
-- MEDIO:   3 problemas (sin domingo, config vacia, Exterior sin boxes)
-- BAJO:    7 problemas (usuario unico, reserva NULL, tablas vacias)
-- FK ROTAS: 0 registros huerfanos
-- DUPLICADOS: 0
-- SECUENCIAS: Todas alineadas
--
-- PROBLEMAS QUE REQUIEREN ACCION INMEDIATA:
-- [ALTO-01] Crear boxes para Acuatico y Exterior
-- [ALTO-02] Corregir clasificacion de modelos (requiere regla de negocio)
--
-- PROBLEMAS QUE REQUIEREN DECISION DE NEGOCIO:
-- [MEDIO-01] Si se quieren reservas domenicales
-- [MEDIO-02] Si la tabla configuracion tiene uso previsto
-- [MEDIO-03] Estrategia para tipo_box Exterior
-- ============================================================================
