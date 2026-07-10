-- ============================================================================
-- CONSULTA DE DETECCION: Servicios activos sin precios configurados
-- ============================================================================
-- Uso: Ejecutar periódicamente o despues de cambios en la tabla servicios.
-- Detecta servicios activos (base/adicional/paquete) que no tienen precios
-- en precios_servicio, excluyendo Aromatizante (que no necesita precios
-- individuales).
--
-- NOTA: Esta consulta NO detecta combinaciones parciales (servicio con
-- precios para algunos tipos pero no todos). Para eso, usar la Parte 4
-- del INFORME_audita_precios_servicio.sql
-- ============================================================================

-- Deteccion simple: servicios activos sin precios
SELECT
  s.id,
  s.nombre,
  s.tipo,
  CASE
    WHEN s.slug = 'aromatizante' THEN 'MANEJADO POR PAQUETES'
    ELSE 'REQUIERE ATENCION'
  END as accion_recomendada
FROM servicios s
LEFT JOIN precios_servicio ps ON ps.servicio_id = s.id
WHERE s.activo = true
  AND s.deleted_at IS NULL
  AND s.tipo IN ('base','adicional','paquete')
  AND ps.id IS NULL
ORDER BY s.tipo, s.id;


-- ============================================================================
-- Deteccion avanzada: servicios con cobertura incompleta por tipo_vehiculo
-- Compara contra el mapa de segmentos esperados por tipo de vehiculo
-- ============================================================================

WITH segmentos_esperados AS (
  -- Mapa seed.py: tipo_vehiculo -> segmentos validos
  SELECT 'moto' as tv_slug, 'pequenio' as seg_slug
  UNION ALL SELECT 'moto','mediano'
  UNION ALL SELECT 'auto','pequenio'
  UNION ALL SELECT 'auto','mediano'
  UNION ALL SELECT 'auto','grande'
  UNION ALL SELECT 'suv','mediano'
  UNION ALL SELECT 'suv','grande'
  UNION ALL SELECT 'pickup','mediano'
  UNION ALL SELECT 'pickup','grande'
  UNION ALL SELECT 'furgon','mediano'
  UNION ALL SELECT 'furgon','grande'
  UNION ALL SELECT 'van','mediano'
  UNION ALL SELECT 'van','grande'
  UNION ALL SELECT 'cuatrimoto','pequenio'
  UNION ALL SELECT 'jetski','pequenio'
  UNION ALL SELECT 'lancha','grande'
  UNION ALL SELECT 'lancha','extra-grande'
  UNION ALL SELECT 'camion','grande'
  UNION ALL SELECT 'camion','extra-grande'
),
servicios_con_tv AS (
  -- Servicios que tienen al menos un precio para un tipo de vehiculo
  SELECT DISTINCT ps.servicio_id, ps.tipo_vehiculo_id
  FROM precios_servicio ps
)
SELECT
  s.id as svc_id,
  s.nombre,
  s.tipo,
  tv.nombre as tipo_veh,
  COUNT(DISTINCT p.id) as precios_existentes,
  (SELECT COUNT(*) FROM segmentos_esperados se WHERE se.tv_slug = tv.slug) * 3 as esperados,
  (SELECT COUNT(*) FROM segmentos_esperados se WHERE se.tv_slug = tv.slug) * 3 - COUNT(DISTINCT p.id) as faltantes
FROM servicios s
CROSS JOIN tipos_vehiculo tv
LEFT JOIN precios_servicio p ON p.servicio_id = s.id AND p.tipo_vehiculo_id = tv.id
WHERE s.activo = true AND s.deleted_at IS NULL
  AND s.tipo IN ('base','adicional','paquete')
  AND s.slug != 'aromatizante'
  AND EXISTS (SELECT 1 FROM servicios_con_tv stv WHERE stv.servicio_id = s.id AND stv.tipo_vehiculo_id = tv.id)
GROUP BY s.id, s.nombre, s.tipo, tv.id, tv.nombre, tv.slug
HAVING COUNT(DISTINCT p.id) < (SELECT COUNT(*) FROM segmentos_esperados se WHERE se.tv_slug = tv.slug) * 3
ORDER BY s.id, tv.id;
