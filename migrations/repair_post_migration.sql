-- =============================================================================
-- MIGRACION: Reparacion de estructura post-migracion MySQL -> PostgreSQL
-- Fecha: 2026-07-09
-- Descripcion: Reconstruye box_tipo_vehiculo y paquete_servicios
--
-- IDEMPOTENTE: Puede ejecutarse multiples veces sin duplicar datos.
-- Utiliza ON CONFLICT DO NOTHING en todas las inserciones.
--
-- FUENTES DE VERDAD:
--   - box_tipo_vehiculo: descripciones de tipos_box en seed.py lineas 372-378
--   - paquete_servicios: descripcion textual de cada paquete en seed.py lineas 163-167
-- =============================================================================

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- PARTE 1: box_tipo_vehiculo
--
-- REGLA: Cada tipo_box tiene una descripcion que indica que tipos de vehiculo
--        son compatibles. Esas descripciones son la fuente de verdad.
--
-- tipos_box (BD actual):
--   11 = Estandar  -> "Box para autos, SUVs y pickups"
--   12 = Grande    -> "Box para vans, furgones y camiones"
--   13 = Moto      -> "Box para motos y cuatrimotos"
--   14 = Acuatico  -> "Box con desague para jet skis y lanchas"
--   15 = Exterior  -> "Box al aire libre para lavados rapidos"
--
-- tipos_vehiculo (BD actual):
--   21=Moto, 22=Auto, 23=SUV, 24=Pickup, 25=Furgon, 26=Van,
--   27=Cuatrimoto, 28=Jet Ski, 29=Lancha/Bote, 30=Camion
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO box_tipo_vehiculo (tipo_box_id, tipo_vehiculo_id)
SELECT tb.id, tv.id
FROM tipos_box tb
CROSS JOIN tipos_vehiculo tv
WHERE
  -- Estandar: "autos, SUVs y pickups"
  (tb.nombre = 'Estandar' AND tv.slug IN ('auto', 'suv', 'pickup'))
  -- Grande: "vans, furgones y camiones"
  OR (tb.nombre = 'Grande' AND tv.slug IN ('furgon', 'van', 'camion'))
  -- Moto: "motos y cuatrimotos"
  OR (tb.nombre = 'Moto' AND tv.slug IN ('moto', 'cuatrimoto'))
  -- Acuatico: "jet skis y lanchas"
  OR (tb.nombre = 'Acuatico' AND tv.slug IN ('jetski', 'lancha'))
  -- Exterior: "lavados rapidos" -> todos los tipos devehiculo terrestres y acuaticos
  OR (tb.nombre = 'Exterior' AND tv.slug IN (
        'moto', 'auto', 'suv', 'pickup', 'furgon', 'van',
        'cuatrimoto', 'jetski', 'lancha', 'camion'
      ))
ON CONFLICT (tipo_box_id, tipo_vehiculo_id) DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- PARTE 2: paquete_servicios
--
-- REGLA: La descripcion de cada paquete en el seed enumera los servicios
--        que lo componen, separados por " + ". El primer servicio listado
--        en la estructura de datos es el es_principal.
--
-- Paquetes (BD actual):
--   59 = Express    -> "Lavado Exterior + Aromatizante"
--   60 = Full       -> "Lavado Completo + Aromatizante"
--   61 = Premium    -> "Detallado Completo + Desinfeccion Ozono"
--   62 = Proteccion Total -> "Pulido + Tratamiento Ceramico"
--   63 = Integral   -> "Detallado Completo + Lavado de Motor + Desinfeccion Ozono"
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO paquete_servicios (paquete_id, servicio_id, es_principal, orden)
SELECT paquete.id, servicio.id, sub.es_principal, sub.orden
FROM
  servicios paquete
  -- Cada composicion: (paquete_slug, servicio_slug, es_principal, orden)
  CROSS JOIN LATERAL (
    VALUES
      ('paquete-express',           'lavado-exterior',    true,  1),
      ('paquete-express',           'aromatizante',       false, 2),
      ('paquete-full',              'lavado-completo',    true,  1),
      ('paquete-full',              'aromatizante',       false, 2),
      ('paquete-premium',           'detallado-completo', true,  1),
      ('paquete-premium',           'desinfeccion-ozono', false, 2),
      ('paquete-proteccion-total',  'pulido',             true,  1),
      ('paquete-proteccion-total',  'tratamiento-ceramico', false, 2),
      ('paquete-integral',          'detallado-completo', true,  1),
      ('paquete-integral',          'lavado-motor',       false, 2),
      ('paquete-integral',          'desinfeccion-ozono', false, 3)
  ) AS sub(paquete_slug, servicio_slug, es_principal, orden)
  INNER JOIN servicios servicio ON servicio.slug = sub.servicio_slug
WHERE paquete.slug = sub.paquete_slug
ON CONFLICT (paquete_id, servicio_id) DO NOTHING;

COMMIT;
