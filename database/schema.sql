-- =============================================
-- Exclusive Auto Detail --- Esquema de Base de Datos
-- MySQL 8.x / InnoDB / UTF8MB4
-- Version: FASE 2 (rediseño del sistema de lavadero)
-- =============================================

CREATE DATABASE IF NOT EXISTS exclusive_autodetail
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE exclusive_autodetail;

-- =============================================
-- NUEVAS TABLAS --- FASE 2
-- =============================================

-- -----------------------------------------
-- 1. tipos_vehiculo
-- -----------------------------------------
CREATE TABLE tipos_vehiculo (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(60)     NOT NULL UNIQUE,
    slug        VARCHAR(60)     NOT NULL UNIQUE,
    descripcion TEXT            NULL,
    icono       VARCHAR(60)     NULL,
    orden       INT UNSIGNED    NOT NULL DEFAULT 0,
    activo      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tv_orden (orden),
    INDEX idx_tv_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 2. categorias_servicio
-- -----------------------------------------
CREATE TABLE categorias_servicio (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(60)     NOT NULL UNIQUE,
    slug                VARCHAR(60)     NOT NULL UNIQUE,
    descripcion         TEXT            NULL,
    icono               VARCHAR(60)     NULL,
    orden               INT UNSIGNED    NOT NULL DEFAULT 0,
    usa_nivel_suciedad  BOOLEAN         NOT NULL DEFAULT FALSE,
    permite_multidias   BOOLEAN         NOT NULL DEFAULT FALSE,
    tiene_subtipos      BOOLEAN         NOT NULL DEFAULT FALSE,
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cs_orden (orden),
    INDEX idx_cs_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 3. tipos_lavado
-- -----------------------------------------
CREATE TABLE tipos_lavado (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(30)     NOT NULL UNIQUE,
    slug                VARCHAR(30)     NOT NULL UNIQUE,
    descripcion         TEXT            NULL,
    orden               INT UNSIGNED    NOT NULL DEFAULT 0,
    es_cerrado          BOOLEAN         NOT NULL DEFAULT FALSE,
    requiere_inspeccion BOOLEAN         NOT NULL DEFAULT FALSE,
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tl_orden (orden),
    INDEX idx_tl_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 4. subtipos_lavado
-- -----------------------------------------
CREATE TABLE subtipos_lavado (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tipo_lavado_id  INT UNSIGNED    NOT NULL,
    nombre          VARCHAR(30)     NOT NULL,
    slug            VARCHAR(30)     NOT NULL,
    descripcion     TEXT            NULL,
    orden           INT UNSIGNED    NOT NULL DEFAULT 0,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_stl_tipo_lavado
        FOREIGN KEY (tipo_lavado_id) REFERENCES tipos_lavado(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_stl_tipo_lavado (tipo_lavado_id),
    INDEX idx_stl_orden (orden)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 5. tipos_detallado
-- -----------------------------------------
CREATE TABLE tipos_detallado (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(60)     NOT NULL UNIQUE,
    slug        VARCHAR(60)     NOT NULL UNIQUE,
    descripcion TEXT            NULL,
    orden       INT UNSIGNED    NOT NULL DEFAULT 0,
    activo      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_td_orden (orden),
    INDEX idx_td_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 6. reglas_precio (matriz central de precios)
-- -----------------------------------------
CREATE TABLE reglas_precio (
    id                      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    categoria_servicio_id   INT UNSIGNED        NOT NULL,
    tipo_vehiculo_id        INT UNSIGNED        NOT NULL,
    tipo_lavado_id          INT UNSIGNED        NULL,
    subtipo_lavado_id       INT UNSIGNED        NULL,
    tipo_detallado_id       INT UNSIGNED        NULL,
    servicio_id             INT UNSIGNED        NULL,
    precio_fijo             DECIMAL(10,2)       NULL,
    precio_estimado         DECIMAL(10,2)       NULL,
    es_precio_estimado      BOOLEAN             NOT NULL DEFAULT FALSE,
    tiempo_estimado_min     INT UNSIGNED        NOT NULL DEFAULT 0,
    dias_bloqueo            INT UNSIGNED        NOT NULL DEFAULT 0,
    descripcion_publica     TEXT                NULL,
    nota_inspeccion         TEXT                NULL,
    activo                  BOOLEAN             NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rp_categoria
        FOREIGN KEY (categoria_servicio_id) REFERENCES categorias_servicio(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rp_tipo_vehiculo
        FOREIGN KEY (tipo_vehiculo_id) REFERENCES tipos_vehiculo(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rp_tipo_lavado
        FOREIGN KEY (tipo_lavado_id) REFERENCES tipos_lavado(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rp_subtipo_lavado
        FOREIGN KEY (subtipo_lavado_id) REFERENCES subtipos_lavado(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rp_tipo_detallado
        FOREIGN KEY (tipo_detallado_id) REFERENCES tipos_detallado(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rp_servicio
        FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_rp_categoria (categoria_servicio_id),
    INDEX idx_rp_vehiculo (tipo_vehiculo_id),
    INDEX idx_rp_combinacion (
        categoria_servicio_id, tipo_vehiculo_id,
        tipo_lavado_id, subtipo_lavado_id,
        tipo_detallado_id, servicio_id
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 7. reserva_items (reemplaza reserva_servicios)
-- -----------------------------------------
CREATE TABLE reserva_items (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id          INT UNSIGNED    NOT NULL,
    tipo_item           VARCHAR(30)     NOT NULL,
    regla_precio_id     INT UNSIGNED    NULL,
    servicio_id         INT UNSIGNED    NULL,
    precio_aplicado     DECIMAL(10,2)   NULL,
    tiempo_aplicado_min INT UNSIGNED    NULL,
    descripcion         TEXT            NULL,
    CONSTRAINT fk_ri_reserva
        FOREIGN KEY (reserva_id) REFERENCES reservas(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ri_regla_precio
        FOREIGN KEY (regla_precio_id) REFERENCES reglas_precio(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_ri_servicio
        FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_ri_reserva (reserva_id),
    INDEX idx_ri_regla_precio (regla_precio_id),
    INDEX idx_ri_tipo_item (tipo_item)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================
-- TABLAS MODIFICADAS --- FASE 2
-- =============================================

-- -----------------------------------------
-- 8. usuarios
-- -----------------------------------------
CREATE TABLE usuarios (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100)    NOT NULL,
    email       VARCHAR(150)    NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol         ENUM('admin','empleado') NOT NULL DEFAULT 'empleado',
    activo      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_usuarios_email (email),
    INDEX idx_usuarios_rol (rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 9. clientes
-- -----------------------------------------
CREATE TABLE clientes (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(80)     NOT NULL,
    apellido      VARCHAR(80)     NOT NULL,
    cedula        VARCHAR(20)     NOT NULL,
    telefono      VARCHAR(20)     NOT NULL,
    email         VARCHAR(150)    NULL,
    observaciones TEXT            NULL,
    created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_clientes_cedula (cedula),
    INDEX idx_clientes_telefono (telefono),
    INDEX idx_clientes_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 10. vehiculos (modificado: FK a tipos_vehiculo, sin booleanos obsoletos)
-- -----------------------------------------
CREATE TABLE vehiculos (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id        INT UNSIGNED NOT NULL,
    tipo_vehiculo     VARCHAR(30)     NOT NULL,
    tipo_vehiculo_id  INT UNSIGNED    NULL,
    marca             VARCHAR(60)     NOT NULL,
    modelo            VARCHAR(60)     NOT NULL,
    anio              SMALLINT UNSIGNED NULL,
    color             VARCHAR(40)     NULL,
    nivel_suciedad    VARCHAR(10)     NULL,
    CONSTRAINT fk_vehiculos_reserva
        FOREIGN KEY (reserva_id) REFERENCES reservas(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_vehiculos_tipo
        FOREIGN KEY (tipo_vehiculo_id) REFERENCES tipos_vehiculo(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_vehiculos_reserva (reserva_id),
    INDEX idx_vehiculos_tipo (tipo_vehiculo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 11. servicios (modificado: FK a categorias_servicio)
-- -----------------------------------------
CREATE TABLE servicios (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre                VARCHAR(120)    NOT NULL,
    descripcion           TEXT            NULL,
    categoria             VARCHAR(30)     NOT NULL,
    categoria_servicio_id INT UNSIGNED    NULL,
    precio                DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    tiempo_estimado_min   INT UNSIGNED    NOT NULL DEFAULT 0,
    activo                BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_servicios_categoria
        FOREIGN KEY (categoria_servicio_id) REFERENCES categorias_servicio(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_servicios_categoria (categoria),
    INDEX idx_servicios_categoria_new (categoria_servicio_id),
    INDEX idx_servicios_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 12. estados_reserva
-- -----------------------------------------
CREATE TABLE estados_reserva (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL UNIQUE,
    color_badge VARCHAR(7)  NOT NULL DEFAULT '#6c757d',
    orden       INT UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 13. reservas (modificado: nuevos FKs + campos)
-- -----------------------------------------
CREATE TABLE reservas (
    id                      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id              INT UNSIGNED NOT NULL,
    estado_id               INT UNSIGNED NOT NULL,
    fecha                   DATE            NOT NULL,
    hora_inicio             TIME            NOT NULL,
    duracion_total_min      INT UNSIGNED    NULL,
    hora_fin                TIME            NULL,
    fecha_fin               DATE            NULL,
    dias_bloqueo            INT UNSIGNED    NULL,
    categoria_servicio_id   INT UNSIGNED    NULL,
    tipo_lavado_id          INT UNSIGNED    NULL,
    subtipo_lavado_id       INT UNSIGNED    NULL,
    tipo_detallado_id       INT UNSIGNED    NULL,
    requiere_inspeccion     BOOLEAN         NOT NULL DEFAULT FALSE,
    precio_estimado         DECIMAL(10,2)   NULL,
    precio_final            DECIMAL(10,2)   NULL,
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,
    observaciones           TEXT            NULL,
    CONSTRAINT fk_reservas_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reservas_estado
        FOREIGN KEY (estado_id) REFERENCES estados_reserva(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reservas_categoria
        FOREIGN KEY (categoria_servicio_id) REFERENCES categorias_servicio(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_reservas_tipo_lavado
        FOREIGN KEY (tipo_lavado_id) REFERENCES tipos_lavado(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_reservas_subtipo_lavado
        FOREIGN KEY (subtipo_lavado_id) REFERENCES subtipos_lavado(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_reservas_tipo_detallado
        FOREIGN KEY (tipo_detallado_id) REFERENCES tipos_detallado(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_reservas_fecha (fecha),
    INDEX idx_reservas_cliente (cliente_id),
    INDEX idx_reservas_estado (estado_id),
    INDEX idx_reservas_categoria (categoria_servicio_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 14. reserva_servicios (tabla pivote legacy)
-- -----------------------------------------
CREATE TABLE reserva_servicios (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id  INT UNSIGNED NOT NULL,
    servicio_id INT UNSIGNED NOT NULL,
    CONSTRAINT fk_rs_reserva
        FOREIGN KEY (reserva_id) REFERENCES reservas(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rs_servicio
        FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_reserva_servicio (reserva_id, servicio_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 15. horarios
-- -----------------------------------------
CREATE TABLE horarios (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    dia_semana      TINYINT UNSIGNED NOT NULL,
    hora_inicio     TIME        NOT NULL,
    hora_fin        TIME        NOT NULL,
    capacidad_maxima INT UNSIGNED NOT NULL DEFAULT 3,
    activo          BOOLEAN     NOT NULL DEFAULT TRUE,
    INDEX idx_horarios_dia (dia_semana)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 16. testimonios
-- -----------------------------------------
CREATE TABLE testimonios (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id          INT UNSIGNED NOT NULL,
    comentario          TEXT            NOT NULL,
    valoracion          TINYINT UNSIGNED NOT NULL,
    vehiculo_descripcion VARCHAR(100) NULL,
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_testimonios_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_testimonios_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- 17. galeria
-- -----------------------------------------
CREATE TABLE galeria (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo      VARCHAR(120)    NOT NULL,
    descripcion TEXT            NULL,
    url_imagen  VARCHAR(255)    NOT NULL,
    tipo        VARCHAR(120)    NOT NULL DEFAULT '',
    activo      BOOLEAN         NOT NULL DEFAULT TRUE,
    orden       INT UNSIGNED    NOT NULL DEFAULT 0,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_galeria_tipo (tipo),
    INDEX idx_galeria_orden (orden)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================
-- INSERTS INICIALES
-- =============================================

-- Estados de reserva
INSERT INTO estados_reserva (nombre, color_badge, orden) VALUES
    ('Pendiente',           '#ffc107', 1),
    ('Confirmada',          '#0d6efd', 2),
    ('Vehiculo recibido',   '#17a2b8', 3),
    ('En proceso',          '#6f42c1', 4),
    ('Lavado terminado',    '#fd7e14', 5),
    ('Esperando retiro',    '#198754', 6),
    ('Finalizada',          '#0dcaf0', 7),
    ('Cancelada',           '#dc3545', 8);

-- Tipos de Vehiculo
INSERT INTO tipos_vehiculo (nombre, slug, icono, orden, activo) VALUES
    ('Auto',                'auto',          NULL, 1, TRUE),
    ('SUV / Camioneta',     'suv-camioneta', NULL, 2, TRUE),
    ('Moto baja cilindrada','moto-baja',     NULL, 3, TRUE),
    ('Moto alta cilindrada','moto-alta',     NULL, 4, TRUE);

-- Categorias de Servicio
INSERT INTO categorias_servicio (nombre, slug, usa_nivel_suciedad, permite_multidias, tiene_subtipos, orden, activo) VALUES
    ('Lavado',                  'lavado',        TRUE,  FALSE, TRUE,  1, TRUE),
    ('Detallado',               'detallado',     FALSE, FALSE, TRUE,  2, TRUE),
    ('Integral',                'integral',      FALSE, TRUE,  FALSE, 3, TRUE),
    ('Tratamientos Especiales', 'tratamientos',  FALSE, FALSE, FALSE, 4, TRUE);

-- Servicios legacy
INSERT INTO servicios (nombre, descripcion, categoria, precio, tiempo_estimado_min, activo) VALUES
    ('Lavado Express',              'Lavado exterior rapido con shampoo neutro, secado y neblinado de neumaticos.',
                                    'lavado_vehiculo', 5000.00, 20, TRUE),
    ('Lavado Detallado',            'Lavado exterior e interior completo, aspirado profundo, lavado de tapizados y plasticos.',
                                    'lavado_vehiculo', 12000.00, 60, TRUE),
    ('Limpieza Integral',           'Lavado Detallado + limpieza de motor, desinfeccion interna y tratamiento de cueros.',
                                    'lavado_vehiculo', 20000.00, 120, TRUE),
    ('Pulido Comercial',            'Pulido mecanico de una etapa, abrillantado y encerado con sellante de alta duracion.',
                                    'tratamiento_pintura', 25000.00, 180, TRUE),
    ('Pulido Tecnico',              'Pulido de dos etapas con correccion de pintura, lustre final y recubrimiento sellador.',
                                    'tratamiento_pintura', 40000.00, 300, TRUE),
    ('Revestimiento Ceramico',      'Aplicacion de recubrimiento ceramico de 9H de dureza, proteccion contra rayos UV y quimicos.',
                                    'tratamiento_pintura', 60000.00, 480, TRUE),
    ('Remocion de Lluvia Acida',    'Tratamiento quimico-mecanico para eliminar manchas de lluvia acida de la pintura y cristales.',
                                    'tratamiento_pintura', 15000.00, 120, TRUE),
    ('Lavado Express de Motos',     'Lavado exterior rapido, cadena y lubricacion basica.',
                                    'lavado_moto', 3000.00, 20, TRUE),
    ('Lavado Detallado de Motos',   'Lavado completo, pulido de carenados, tratamiento de cromados y acondicionamiento de cadena.',
                                    'lavado_moto', 8000.00, 60, TRUE);

-- Usuario administrador por defecto
-- password: Admin1234!
INSERT INTO usuarios (nombre, email, password_hash, rol, activo) VALUES
    ('Administrador', 'admin@exclusiveautodetail.com',
     '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Ql.q0Yf0Lm8GJHb3dF5qX7y0ZKa',
     'admin', TRUE);

-- Horarios: lunes a sabado, 07:00 a 17:00, capacidad 3 por bloque
INSERT INTO horarios (dia_semana, hora_inicio, hora_fin, capacidad_maxima, activo) VALUES
    (1, '07:00:00', '17:00:00', 3, TRUE),
    (2, '07:00:00', '17:00:00', 3, TRUE),
    (3, '07:00:00', '17:00:00', 3, TRUE),
    (4, '07:00:00', '17:00:00', 3, TRUE),
    (5, '07:00:00', '17:00:00', 3, TRUE),
    (6, '07:00:00', '17:00:00', 3, TRUE);
