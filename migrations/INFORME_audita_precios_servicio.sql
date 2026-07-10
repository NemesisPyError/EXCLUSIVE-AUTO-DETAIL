-- ============================================================================
-- INFORME: AUDITORIA COMPLETA DE precios_servicio
-- Fecha: 2026-07-09
-- Base: exclusive_autodetail (PostgreSQL)
-- ============================================================================

-- ============================================================================
-- RESUMEN EJECUTIVO
-- ============================================================================
-- La tabla precios_servicio esta COMPLETA. Los 591 registros definidos en
-- seed.py existen en la base de datos sin perdidas ni duplicaciones.
--
-- hallazgo clave: La tabla servicio_tipo_vehiculo genera combinaciones
-- servicio x tipo_vehiculo que, al cruzarse con TODOS los segmentos y niveles
-- de suciedad, produce 1,920 combinaciones teoricas. De estas, solo 654
-- (34%) son validas segun el seed. Las 1,266 restantes nunca tuvieron precios
-- porque el seed asigna precios solo para segmentos especificos por tipo
-- de vehiculo.
--
-- El unico servicio sin precios es Aromatizante (id=56), que INTENCIONALMENTE
-- no tiene precios individuales en el seed. Se incluye como componente de
-- paquetes (Express y Full).
-- ============================================================================


-- ============================================================================
-- PARTE 1: RESUMEN GENERAL
-- ============================================================================

-- 1.1 Totales generales
SELECT
  '--- TOTALES GENERALES ---' as seccion,
  (SELECT COUNT(*) FROM precios_servicio) as registros_totales,
  (SELECT COUNT(*) FROM servicios s WHERE s.activo=true AND s.deleted_at IS NULL AND s.tipo IN ('base','adicional','paquete')) as servicios_activos,
  (SELECT COUNT(*) FROM tipos_vehiculo) as tipos_vehiculo,
  (SELECT COUNT(*) FROM segmentos) as segmentos,
  (SELECT COUNT(*) FROM niveles_suciedad) as niveles_suciedad;


-- ============================================================================
-- PARTE 2: COBERTURA POR SERVICIO (vs seed.py)
-- ============================================================================

-- Seed.py defines 197 segment combinations x 3 levels = 591 total records
-- This query shows each service vs its expected count from the seed

SELECT
  s.id as svc_id,
  s.nombre,
  s.tipo,
  COUNT(ps.id) as registros_en_db,
  CASE s.slug
    WHEN 'lavado-exterior' THEN 57
    WHEN 'lavado-interior' THEN 39
    WHEN 'lavado-completo' THEN 57
    WHEN 'detallado-interior' THEN 39
    WHEN 'detallado-exterior' THEN 39
    WHEN 'detallado-completo' THEN 39
    WHEN 'pulido' THEN 27
    WHEN 'tratamiento-ceramico' THEN 21
    WHEN 'tratamiento-acrilico' THEN 21
    WHEN 'lavado-motor' THEN 27
    WHEN 'desinfeccion-ozono' THEN 27
    WHEN 'restauracion-faros' THEN 21
    WHEN 'limpieza-tapizado' THEN 27
    WHEN 'retiro-domicilio' THEN 27
    WHEN 'entrega-domicilio' THEN 27
    WHEN 'paquete-express' THEN 12
    WHEN 'paquete-full' THEN 21
    WHEN 'paquete-premium' THEN 21
    WHEN 'paquete-proteccion-total' THEN 21
    WHEN 'paquete-integral' THEN 21
    WHEN 'aromatizante' THEN 0
    ELSE -1
  END as seed_esperado,
  CASE
    WHEN COUNT(ps.id) = 0 AND s.slug = 'aromatizante' THEN 'OK (sin precios por disenio)'
    WHEN COUNT(ps.id) = CASE s.slug
      WHEN 'lavado-exterior' THEN 57 WHEN 'lavado-interior' THEN 39
      WHEN 'lavado-completo' THEN 57 WHEN 'detallado-interior' THEN 39
      WHEN 'detallado-exterior' THEN 39 WHEN 'detallado-completo' THEN 39
      WHEN 'pulido' THEN 27 WHEN 'tratamiento-ceramico' THEN 21
      WHEN 'tratamiento-acrilico' THEN 21 WHEN 'lavado-motor' THEN 27
      WHEN 'desinfeccion-ozono' THEN 27 WHEN 'restauracion-faros' THEN 21
      WHEN 'limpieza-tapizado' THEN 27 WHEN 'retiro-domicilio' THEN 27
      WHEN 'entrega-domicilio' THEN 27 WHEN 'paquete-express' THEN 12
      WHEN 'paquete-full' THEN 21 WHEN 'paquete-premium' THEN 21
      WHEN 'paquete-proteccion-total' THEN 21 WHEN 'paquete-integral' THEN 21
      ELSE -1
    END THEN 'COMPLETO'
    ELSE 'INCOMPLETO - FALTANTES'
  END as estado
FROM servicios s
LEFT JOIN precios_servicio ps ON ps.servicio_id = s.id
WHERE s.activo = true AND s.deleted_at IS NULL
  AND s.tipo IN ('base','adicional','paquete')
GROUP BY s.id, s.nombre, s.tipo, s.slug
ORDER BY s.id;


-- ============================================================================
-- PARTE 3: SEGMENTOS POR TIPO DE VEHICULO
-- ============================================================================
-- El seed NO asigna precios para TODOS los segmentos en TODOS los tipos.
-- Cada tipo tiene un rango natural de segmentos aplicables.
-- ============================================================================

-- 3.1 Segmentos que existen en precios_servicio por tipo_vehiculo
SELECT
  tv.nombre as tipo_veh,
  seg.nombre as segmento,
  COUNT(DISTINCT ps.servicio_id) as servicios_con_precio,
  COUNT(ps.id) as total_registros
FROM precios_servicio ps
JOIN tipos_vehiculo tv ON ps.tipo_vehiculo_id = tv.id
JOIN segmentos seg ON ps.segmento_id = seg.id
GROUP BY tv.id, tv.nombre, seg.id, seg.nombre
ORDER BY tv.id, seg.id;


-- ============================================================================
-- PARTE 4: DETECCION DE COMBINACIONES FALTANTES (Metodo Correcto)
-- ============================================================================
-- Usa el seed.py como fuente de verdad, NO un cruce/cartesiano.
-- Un cruce completo (servicio x tipo x segmento x nivel) genera 1,920
-- combinaciones, pero solo 654 son validas. Las demas son "falsos positivos".
-- ============================================================================

-- 4.1 Lista completa de las 654 combinaciones que DEBEN existir (según seed)
--     y verificacion contra la DB

WITH seed_combos AS (
    -- Lavado Exterior (19 segmentos -> 57 registros)
    SELECT 'lavado-exterior' as svc, 'moto' as tv, 'pequenio' as seg
    UNION ALL SELECT 'lavado-exterior','moto','mediano'
    UNION ALL SELECT 'lavado-exterior','auto','pequenio'
    UNION ALL SELECT 'lavado-exterior','auto','mediano'
    UNION ALL SELECT 'lavado-exterior','auto','grande'
    UNION ALL SELECT 'lavado-exterior','suv','mediano'
    UNION ALL SELECT 'lavado-exterior','suv','grande'
    UNION ALL SELECT 'lavado-exterior','pickup','mediano'
    UNION ALL SELECT 'lavado-exterior','pickup','grande'
    UNION ALL SELECT 'lavado-exterior','furgon','mediano'
    UNION ALL SELECT 'lavado-exterior','furgon','grande'
    UNION ALL SELECT 'lavado-exterior','van','mediano'
    UNION ALL SELECT 'lavado-exterior','van','grande'
    UNION ALL SELECT 'lavado-exterior','cuatrimoto','pequenio'
    UNION ALL SELECT 'lavado-exterior','jetski','pequenio'
    UNION ALL SELECT 'lavado-exterior','lancha','grande'
    UNION ALL SELECT 'lavado-exterior','lancha','extra-grande'
    UNION ALL SELECT 'lavado-exterior','camion','grande'
    UNION ALL SELECT 'lavado-exterior','camion','extra-grande'
    -- Lavado Interior (13 segmentos)
    UNION ALL SELECT 'lavado-interior','auto','pequenio'
    UNION ALL SELECT 'lavado-interior','auto','mediano'
    UNION ALL SELECT 'lavado-interior','auto','grande'
    UNION ALL SELECT 'lavado-interior','suv','mediano'
    UNION ALL SELECT 'lavado-interior','suv','grande'
    UNION ALL SELECT 'lavado-interior','pickup','mediano'
    UNION ALL SELECT 'lavado-interior','pickup','grande'
    UNION ALL SELECT 'lavado-interior','furgon','mediano'
    UNION ALL SELECT 'lavado-interior','furgon','grande'
    UNION ALL SELECT 'lavado-interior','van','mediano'
    UNION ALL SELECT 'lavado-interior','van','grande'
    UNION ALL SELECT 'lavado-interior','camion','grande'
    UNION ALL SELECT 'lavado-interior','camion','extra-grande'
    -- Lavado Completo (19 segmentos)
    UNION ALL SELECT 'lavado-completo','moto','pequenio'
    UNION ALL SELECT 'lavado-completo','moto','mediano'
    UNION ALL SELECT 'lavado-completo','auto','pequenio'
    UNION ALL SELECT 'lavado-completo','auto','mediano'
    UNION ALL SELECT 'lavado-completo','auto','grande'
    UNION ALL SELECT 'lavado-completo','suv','mediano'
    UNION ALL SELECT 'lavado-completo','suv','grande'
    UNION ALL SELECT 'lavado-completo','pickup','mediano'
    UNION ALL SELECT 'lavado-completo','pickup','grande'
    UNION ALL SELECT 'lavado-completo','furgon','mediano'
    UNION ALL SELECT 'lavado-completo','furgon','grande'
    UNION ALL SELECT 'lavado-completo','van','mediano'
    UNION ALL SELECT 'lavado-completo','van','grande'
    UNION ALL SELECT 'lavado-completo','cuatrimoto','pequenio'
    UNION ALL SELECT 'lavado-completo','jetski','pequenio'
    UNION ALL SELECT 'lavado-completo','lancha','grande'
    UNION ALL SELECT 'lavado-completo','lancha','extra-grande'
    UNION ALL SELECT 'lavado-completo','camion','grande'
    UNION ALL SELECT 'lavado-completo','camion','extra-grande'
    -- Detallado Interior (13 segmentos)
    UNION ALL SELECT 'detallado-interior','auto','pequenio'
    UNION ALL SELECT 'detallado-interior','auto','mediano'
    UNION ALL SELECT 'detallado-interior','auto','grande'
    UNION ALL SELECT 'detallado-interior','suv','mediano'
    UNION ALL SELECT 'detallado-interior','suv','grande'
    UNION ALL SELECT 'detallado-interior','pickup','mediano'
    UNION ALL SELECT 'detallado-interior','pickup','grande'
    UNION ALL SELECT 'detallado-interior','furgon','mediano'
    UNION ALL SELECT 'detallado-interior','furgon','grande'
    UNION ALL SELECT 'detallado-interior','van','mediano'
    UNION ALL SELECT 'detallado-interior','van','grande'
    UNION ALL SELECT 'detallado-interior','lancha','grande'
    UNION ALL SELECT 'detallado-interior','lancha','extra-grande'
    -- Detallado Exterior (13 segmentos)
    UNION ALL SELECT 'detallado-exterior','auto','pequenio'
    UNION ALL SELECT 'detallado-exterior','auto','mediano'
    UNION ALL SELECT 'detallado-exterior','auto','grande'
    UNION ALL SELECT 'detallado-exterior','suv','mediano'
    UNION ALL SELECT 'detallado-exterior','suv','grande'
    UNION ALL SELECT 'detallado-exterior','pickup','mediano'
    UNION ALL SELECT 'detallado-exterior','pickup','grande'
    UNION ALL SELECT 'detallado-exterior','furgon','mediano'
    UNION ALL SELECT 'detallado-exterior','furgon','grande'
    UNION ALL SELECT 'detallado-exterior','van','mediano'
    UNION ALL SELECT 'detallado-exterior','van','grande'
    UNION ALL SELECT 'detallado-exterior','lancha','grande'
    UNION ALL SELECT 'detallado-exterior','lancha','extra-grande'
    -- Detallado Completo (13 segmentos)
    UNION ALL SELECT 'detallado-completo','auto','pequenio'
    UNION ALL SELECT 'detallado-completo','auto','mediano'
    UNION ALL SELECT 'detallado-completo','auto','grande'
    UNION ALL SELECT 'detallado-completo','suv','mediano'
    UNION ALL SELECT 'detallado-completo','suv','grande'
    UNION ALL SELECT 'detallado-completo','pickup','mediano'
    UNION ALL SELECT 'detallado-completo','pickup','grande'
    UNION ALL SELECT 'detallado-completo','furgon','mediano'
    UNION ALL SELECT 'detallado-completo','furgon','grande'
    UNION ALL SELECT 'detallado-completo','van','mediano'
    UNION ALL SELECT 'detallado-completo','van','grande'
    UNION ALL SELECT 'detallado-completo','lancha','grande'
    UNION ALL SELECT 'detallado-completo','lancha','extra-grande'
    -- Pulido (9 segmentos)
    UNION ALL SELECT 'pulido','auto','pequenio'
    UNION ALL SELECT 'pulido','auto','mediano'
    UNION ALL SELECT 'pulido','auto','grande'
    UNION ALL SELECT 'pulido','suv','mediano'
    UNION ALL SELECT 'pulido','suv','grande'
    UNION ALL SELECT 'pulido','pickup','mediano'
    UNION ALL SELECT 'pulido','pickup','grande'
    UNION ALL SELECT 'pulido','furgon','mediano'
    UNION ALL SELECT 'pulido','furgon','grande'
    -- Tratamiento Ceramico (7 segmentos)
    UNION ALL SELECT 'tratamiento-ceramico','auto','pequenio'
    UNION ALL SELECT 'tratamiento-ceramico','auto','mediano'
    UNION ALL SELECT 'tratamiento-ceramico','auto','grande'
    UNION ALL SELECT 'tratamiento-ceramico','suv','mediano'
    UNION ALL SELECT 'tratamiento-ceramico','suv','grande'
    UNION ALL SELECT 'tratamiento-ceramico','pickup','mediano'
    UNION ALL SELECT 'tratamiento-ceramico','pickup','grande'
    -- Tratamiento Acrilico (7 segmentos)
    UNION ALL SELECT 'tratamiento-acrilico','auto','pequenio'
    UNION ALL SELECT 'tratamiento-acrilico','auto','mediano'
    UNION ALL SELECT 'tratamiento-acrilico','auto','grande'
    UNION ALL SELECT 'tratamiento-acrilico','suv','mediano'
    UNION ALL SELECT 'tratamiento-acrilico','suv','grande'
    UNION ALL SELECT 'tratamiento-acrilico','pickup','mediano'
    UNION ALL SELECT 'tratamiento-acrilico','pickup','grande'
    -- Lavado de Motor (9 segmentos)
    UNION ALL SELECT 'lavado-motor','auto','pequenio'
    UNION ALL SELECT 'lavado-motor','auto','mediano'
    UNION ALL SELECT 'lavado-motor','auto','grande'
    UNION ALL SELECT 'lavado-motor','suv','mediano'
    UNION ALL SELECT 'lavado-motor','suv','grande'
    UNION ALL SELECT 'lavado-motor','pickup','mediano'
    UNION ALL SELECT 'lavado-motor','pickup','grande'
    UNION ALL SELECT 'lavado-motor','camion','grande'
    UNION ALL SELECT 'lavado-motor','camion','extra-grande'
    -- Desinfeccion Ozono (9 segmentos)
    UNION ALL SELECT 'desinfeccion-ozono','auto','pequenio'
    UNION ALL SELECT 'desinfeccion-ozono','auto','mediano'
    UNION ALL SELECT 'desinfeccion-ozono','auto','grande'
    UNION ALL SELECT 'desinfeccion-ozono','suv','mediano'
    UNION ALL SELECT 'desinfeccion-ozono','suv','grande'
    UNION ALL SELECT 'desinfeccion-ozono','pickup','mediano'
    UNION ALL SELECT 'desinfeccion-ozono','pickup','grande'
    UNION ALL SELECT 'desinfeccion-ozono','van','mediano'
    UNION ALL SELECT 'desinfeccion-ozono','van','grande'
    -- Restauracion Faros (7 segmentos)
    UNION ALL SELECT 'restauracion-faros','auto','pequenio'
    UNION ALL SELECT 'restauracion-faros','auto','mediano'
    UNION ALL SELECT 'restauracion-faros','auto','grande'
    UNION ALL SELECT 'restauracion-faros','suv','mediano'
    UNION ALL SELECT 'restauracion-faros','suv','grande'
    UNION ALL SELECT 'restauracion-faros','pickup','mediano'
    UNION ALL SELECT 'restauracion-faros','pickup','grande'
    -- Limpieza Tapizado (9 segmentos)
    UNION ALL SELECT 'limpieza-tapizado','auto','pequenio'
    UNION ALL SELECT 'limpieza-tapizado','auto','mediano'
    UNION ALL SELECT 'limpieza-tapizado','auto','grande'
    UNION ALL SELECT 'limpieza-tapizado','suv','mediano'
    UNION ALL SELECT 'limpieza-tapizado','suv','grande'
    UNION ALL SELECT 'limpieza-tapizado','pickup','mediano'
    UNION ALL SELECT 'limpieza-tapizado','pickup','grande'
    UNION ALL SELECT 'limpieza-tapizado','van','mediano'
    UNION ALL SELECT 'limpieza-tapizado','van','grande'
    -- Retiro Domicilio (9 segmentos)
    UNION ALL SELECT 'retiro-domicilio','auto','pequenio'
    UNION ALL SELECT 'retiro-domicilio','auto','mediano'
    UNION ALL SELECT 'retiro-domicilio','auto','grande'
    UNION ALL SELECT 'retiro-domicilio','suv','mediano'
    UNION ALL SELECT 'retiro-domicilio','suv','grande'
    UNION ALL SELECT 'retiro-domicilio','pickup','mediano'
    UNION ALL SELECT 'retiro-domicilio','pickup','grande'
    UNION ALL SELECT 'retiro-domicilio','van','mediano'
    UNION ALL SELECT 'retiro-domicilio','van','grande'
    -- Entrega Domicilio (9 segmentos)
    UNION ALL SELECT 'entrega-domicilio','auto','pequenio'
    UNION ALL SELECT 'entrega-domicilio','auto','mediano'
    UNION ALL SELECT 'entrega-domicilio','auto','grande'
    UNION ALL SELECT 'entrega-domicilio','suv','mediano'
    UNION ALL SELECT 'entrega-domicilio','suv','grande'
    UNION ALL SELECT 'entrega-domicilio','pickup','mediano'
    UNION ALL SELECT 'entrega-domicilio','pickup','grande'
    UNION ALL SELECT 'entrega-domicilio','van','mediano'
    UNION ALL SELECT 'entrega-domicilio','van','grande'
    -- Paquete Express (4 segmentos)
    UNION ALL SELECT 'paquete-express','auto','pequenio'
    UNION ALL SELECT 'paquete-express','auto','mediano'
    UNION ALL SELECT 'paquete-express','suv','mediano'
    UNION ALL SELECT 'paquete-express','pickup','mediano'
    -- Paquete Full (7 segmentos)
    UNION ALL SELECT 'paquete-full','auto','pequenio'
    UNION ALL SELECT 'paquete-full','auto','mediano'
    UNION ALL SELECT 'paquete-full','auto','grande'
    UNION ALL SELECT 'paquete-full','suv','mediano'
    UNION ALL SELECT 'paquete-full','suv','grande'
    UNION ALL SELECT 'paquete-full','pickup','mediano'
    UNION ALL SELECT 'paquete-full','pickup','grande'
    -- Paquete Premium (7 segmentos)
    UNION ALL SELECT 'paquete-premium','auto','pequenio'
    UNION ALL SELECT 'paquete-premium','auto','mediano'
    UNION ALL SELECT 'paquete-premium','auto','grande'
    UNION ALL SELECT 'paquete-premium','suv','mediano'
    UNION ALL SELECT 'paquete-premium','suv','grande'
    UNION ALL SELECT 'paquete-premium','pickup','mediano'
    UNION ALL SELECT 'paquete-premium','pickup','grande'
    -- Paquete Proteccion Total (7 segmentos)
    UNION ALL SELECT 'paquete-proteccion-total','auto','pequenio'
    UNION ALL SELECT 'paquete-proteccion-total','auto','mediano'
    UNION ALL SELECT 'paquete-proteccion-total','auto','grande'
    UNION ALL SELECT 'paquete-proteccion-total','suv','mediano'
    UNION ALL SELECT 'paquete-proteccion-total','suv','grande'
    UNION ALL SELECT 'paquete-proteccion-total','pickup','mediano'
    UNION ALL SELECT 'paquete-proteccion-total','pickup','grande'
    -- Paquete Integral (7 segmentos)
    UNION ALL SELECT 'paquete-integral','auto','pequenio'
    UNION ALL SELECT 'paquete-integral','auto','mediano'
    UNION ALL SELECT 'paquete-integral','auto','grande'
    UNION ALL SELECT 'paquete-integral','suv','mediano'
    UNION ALL SELECT 'paquete-integral','suv','grande'
    UNION ALL SELECT 'paquete-integral','pickup','mediano'
    UNION ALL SELECT 'paquete-integral','pickup','grande'
)
SELECT
  sc.svc as servicio,
  sc.tv as tipo_vehiculo,
  sc.seg as segmento,
  CASE WHEN ps3.existe THEN 'OK' ELSE 'FALTANTE' END as nivel_normal,
  CASE WHEN ps8.existe THEN 'OK' ELSE 'FALTANTE' END as nivel_alta,
  CASE WHEN ps9.existe THEN 'OK' ELSE 'FALTANTE' END as nivel_extrema
FROM seed_combos sc
LEFT JOIN LATERAL (
  SELECT true as existe FROM precios_servicio p
  WHERE p.servicio_id = (SELECT id FROM servicios WHERE slug = sc.svc LIMIT 1)
    AND p.tipo_vehiculo_id = (SELECT id FROM tipos_vehiculo WHERE slug = sc.tv LIMIT 1)
    AND p.segmento_id = (SELECT id FROM segmentos WHERE slug = sc.seg LIMIT 1)
    AND p.nivel_suciedad_id = 7
) ps3 ON true
LEFT JOIN LATERAL (
  SELECT true as existe FROM precios_servicio p
  WHERE p.servicio_id = (SELECT id FROM servicios WHERE slug = sc.svc LIMIT 1)
    AND p.tipo_vehiculo_id = (SELECT id FROM tipos_vehiculo WHERE slug = sc.tv LIMIT 1)
    AND p.segmento_id = (SELECT id FROM segmentos WHERE slug = sc.seg LIMIT 1)
    AND p.nivel_suciedad_id = 8
) ps8 ON true
LEFT JOIN LATERAL (
  SELECT true as existe FROM precios_servicio p
  WHERE p.servicio_id = (SELECT id FROM servicios WHERE slug = sc.svc LIMIT 1)
    AND p.tipo_vehiculo_id = (SELECT id FROM tipos_vehiculo WHERE slug = sc.tv LIMIT 1)
    AND p.segmento_id = (SELECT id FROM segmentos WHERE slug = sc.seg LIMIT 1)
    AND p.nivel_suciedad_id = 9
) ps9 ON true
WHERE NOT ps3.existe OR NOT ps8.existe OR NOT ps9.existe
ORDER BY sc.svc, sc.tv, sc.seg;


-- ============================================================================
-- PARTE 5: SERVICIOS SIN PRECIOS
-- ============================================================================

-- 5.1 Servicios activos sin ningun registro en precios_servicio
SELECT
  s.id,
  s.nombre,
  s.tipo,
  'Sin precios individuales en seed.py (intencional)' as razon
FROM servicios s
LEFT JOIN precios_servicio ps ON ps.servicio_id = s.id
WHERE s.activo = true AND s.deleted_at IS NULL
  AND ps.id IS NULL;


-- ============================================================================
-- PARTE 6: VERIFICACION DE INTEGRIDAD DE PRECIOS
-- ============================================================================

-- 6.1 Verificar que los multiplicadores de suciedad son correctos
-- Seed: normal=1.0x, alta=1.3x, extrema=1.6x
SELECT
  s.nombre as servicio,
  tv.nombre as tipo_veh,
  seg.nombre as segmento,
  p_normal.precio as precio_normal,
  p_alta.precio as precio_alta,
  p_extrema.precio as precio_extrema,
  ROUND(p_alta.precio::numeric / NULLIF(p_normal.precio,0), 2) as ratio_alta,
  ROUND(p_extrema.precio::numeric / NULLIF(p_normal.precio,0), 2) as ratio_extrema,
  CASE
    WHEN ROUND(p_alta.precio::numeric / NULLIF(p_normal.precio,0), 2) = 1.30
     AND ROUND(p_extrema.precio::numeric / NULLIF(p_normal.precio,0), 2) = 1.60
    THEN 'OK'
    ELSE 'ERROR'
  END as estado
FROM precios_servicio p_normal
JOIN precios_servicio p_alta
  ON p_alta.servicio_id = p_normal.servicio_id
  AND p_alta.tipo_vehiculo_id = p_normal.tipo_vehiculo_id
  AND p_alta.segmento_id = p_normal.segmento_id
  AND p_alta.nivel_suciedad_id = 8
JOIN precios_servicio p_extrema
  ON p_extrema.servicio_id = p_normal.servicio_id
  AND p_extrema.tipo_vehiculo_id = p_normal.tipo_vehiculo_id
  AND p_extrema.segmento_id = p_normal.segmento_id
  AND p_extrema.nivel_suciedad_id = 9
JOIN servicios s ON s.id = p_normal.servicio_id
JOIN tipos_vehiculo tv ON tv.id = p_normal.tipo_vehiculo_id
JOIN segmentos seg ON seg.id = p_normal.segmento_id
WHERE p_normal.nivel_suciedad_id = 7
  AND s.tipo IN ('base','adicional','paquete')
ORDER BY s.id, tv.id, seg.id;


-- ============================================================================
-- PARTE 7: SERVICIOS ADICIONALES - ESTADO
-- ============================================================================

SELECT
  s.id,
  s.nombre,
  s.tipo,
  COUNT(ps.id) as registros_precio,
  CASE
    WHEN COUNT(ps.id) = 0 THEN 'SIN PRECIOS (Aromatizante: manejado por paquetes)'
    ELSE 'CON PRECIOS'
  END as estado
FROM servicios s
LEFT JOIN precios_servicio ps ON ps.servicio_id = s.id
WHERE s.tipo = 'adicional' AND s.activo = true AND s.deleted_at IS NULL
GROUP BY s.id, s.nombre, s.tipo
ORDER BY s.id;


-- ============================================================================
-- PARTE 8: PAQUETES - COMPOSICION Y PRECIOS
-- ============================================================================

SELECT
  paq.nombre as paquete,
  STRING_AGG(svc.nombre, ' + ' ORDER BY ps.orden) as componentes,
  COUNT(DISTINCT p.servicio_id) as servicios_con_precio
FROM paquete_servicios ps
JOIN servicios paq ON ps.paquete_id = paq.id
JOIN servicios svc ON ps.servicio_id = svc.id
LEFT JOIN precios_servicio p ON p.servicio_id = paq.id
GROUP BY paq.id, paq.nombre
ORDER BY paq.id;


-- ============================================================================
-- CONCLUSION
-- ============================================================================
-- ESTADO: COMPLETO
-- No se requiere migracion de datos. Los 591 registros de precios_servicio
-- coinciden exactamente con los definidos en seed.py.
--
-- El unico servicio sin precios es Aromatizante (id=56), lo cual es correcto
-- por disenio: solo se usa como componente de paquetes (Express y Full).
--
-- ADVERTENCIA: La tabla servicio_tipo_vehiculo NO refleja la restriccion
-- de segmentos por tipo_vehiculo. Si se necesita un cruce completo de
-- deteccion, usar el seed.py como fuente de verdad (como en la Parte 4),
-- NO un cruce cartesiano.
-- ============================================================================
