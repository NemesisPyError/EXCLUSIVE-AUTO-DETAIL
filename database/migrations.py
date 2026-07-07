from sqlalchemy import inspect, text
from extensions import db


def _crear_indices_faltantes(insp):
    existing_tables = set(insp.get_table_names())
    indices_existentes = {}

    for table_name in existing_tables:
        try:
            indices_existentes[table_name] = set()
            for idx in insp.get_indexes(table_name):
                cols_key = '_'.join(idx['column_names'])
                indices_existentes[table_name].add(cols_key)
        except Exception:
            continue

    def _crear_si_falta(table, cols_key, ddl):
        if table not in existing_tables:
            return
        if table not in indices_existentes or cols_key not in indices_existentes[table]:
            try:
                with db.engine.begin() as conn:
                    conn.execute(text(ddl))
            except Exception:
                pass

    _crear_si_falta(
        'reservas', 'fecha_estado_id',
        "CREATE INDEX idx_reservas_fecha_estado ON reservas(fecha, estado_id)"
    )
    _crear_si_falta(
        'reservas', 'fecha_hora_inicio',
        "CREATE INDEX idx_reservas_fecha_hora ON reservas(fecha, hora_inicio)"
    )
    _crear_si_falta(
        'reservas', 'created_at',
        "CREATE INDEX idx_reservas_created ON reservas(created_at)"
    )
    _crear_si_falta(
        'reserva_factores_tiempo', 'reserva_id',
        "CREATE INDEX idx_rft_reserva ON reserva_factores_tiempo(reserva_id)"
    )
    _crear_si_falta(
        'reserva_factores_tiempo', 'factor_tiempo_id',
        "CREATE INDEX idx_rft_factor ON reserva_factores_tiempo(factor_tiempo_id)"
    )
    _crear_si_falta(
        'factores_tiempo', 'tipo_activo',
        "CREATE INDEX idx_ft_tipo_activo ON factores_tiempo(tipo, activo)"
    )
    _crear_si_falta(
        'testimonios', 'created_at',
        "CREATE INDEX idx_testimonios_created ON testimonios(created_at)"
    )
    _crear_si_falta(
        'clientes', 'created_at',
        "CREATE INDEX idx_clientes_created ON clientes(created_at)"
    )
    _crear_si_falta(
        'galeria_categoria', 'activo_orden',
        "CREATE INDEX idx_gc_activo_orden ON galeria_categoria(activo, orden)"
    )
    _crear_si_falta(
        'galeria', 'activo_orden',
        "CREATE INDEX idx_galeria_activo_orden ON galeria(activo, orden)"
    )


def asegurar_esquema():
    insp = inspect(db.engine)

    if 'clientes' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('clientes')]
        if 'cedula' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE clientes ADD COLUMN cedula VARCHAR(20) NOT NULL DEFAULT ''"
                ))

    if 'reservas' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('reservas')]
        if 'duracion_total_min' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN duracion_total_min INT NULL"
                ))
        if 'hora_fin' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN hora_fin TIME NULL"
                ))
        if 'fecha_fin' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN fecha_fin DATE NULL"
                ))
        if 'dias_bloqueo' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN dias_bloqueo INT NULL"
                ))
        if 'categoria_servicio_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN categoria_servicio_id INT NULL"
                ))
        if 'tipo_lavado_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN tipo_lavado_id INT NULL"
                ))
        if 'subtipo_lavado_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN subtipo_lavado_id INT NULL"
                ))
        if 'tipo_detallado_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN tipo_detallado_id INT NULL"
                ))
        if 'requiere_inspeccion' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN requiere_inspeccion BOOLEAN NOT NULL DEFAULT FALSE"
                ))
        if 'precio_estimado' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN precio_estimado DECIMAL(10,2) NULL"
                ))
        if 'precio_final' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN precio_final DECIMAL(10,2) NULL"
                ))
        if 'asignado_a_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN asignado_a_id INT NULL"
                ))
        if 'confirmacion_token' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE reservas ADD COLUMN confirmacion_token VARCHAR(128) NULL"
                ))
                conn.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_reservas_confirmacion_token ON reservas(confirmacion_token)"
                ))

    if 'servicios' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('servicios')]
        if 'categoria_servicio_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE servicios ADD COLUMN categoria_servicio_id INT NULL"
                ))

    if 'vehiculos' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('vehiculos')]
        if 'tipo_vehiculo_id' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE vehiculos ADD COLUMN tipo_vehiculo_id INT NULL"
                ))

    if 'usuarios' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('usuarios')]
        if 'login_attempts' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE usuarios ADD COLUMN login_attempts INT NOT NULL DEFAULT 0"
                ))
        if 'locked_until' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE usuarios ADD COLUMN locked_until DATETIME NULL"
                ))
        if 'session_version' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE usuarios ADD COLUMN session_version INT NOT NULL DEFAULT 0"
                ))
        if 'reset_token' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE usuarios ADD COLUMN reset_token VARCHAR(128) NULL"
                ))
                conn.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_reset_token ON usuarios(reset_token)"
                ))
        if 'reset_token_expiry' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE usuarios ADD COLUMN reset_token_expiry DATETIME NULL"
                ))

    if 'galeria' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('galeria')]
        if 'url_thumb' not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE galeria ADD COLUMN url_thumb VARCHAR(255) NULL"
                ))

    _crear_indices_faltantes(insp)


def migrar_galeria_categorias():
    from models.galeria import Galeria
    from models.galeria_categoria import GaleriaCategoria

    insp = inspect(db.engine)
    if 'galeria' not in insp.get_table_names():
        return

    columnas = [c['name'] for c in insp.get_columns('galeria')]
    if 'categoria_id' not in columnas:
        try:
            with db.engine.begin() as conn:
                conn.execute(text(
                    'ALTER TABLE galeria ADD COLUMN categoria_id INT NULL'
                ))
        except Exception:
            return

    if 'galeria_categoria' not in insp.get_table_names():
        return

    try:
        pendientes = Galeria.query.filter(
            (Galeria.categoria_id.is_(None)) & (Galeria.tipo != '') & (Galeria.tipo.isnot(None))
        ).all()

        cache = {c.nombre: c for c in GaleriaCategoria.query.all()}
        orden_max = db.session.query(db.func.max(GaleriaCategoria.orden)).scalar() or 0

        for item in pendientes:
            cat = cache.get(item.tipo)
            if not cat:
                orden_max += 1
                cat = GaleriaCategoria(nombre=item.tipo, orden=orden_max, activo=True)
                db.session.add(cat)
                db.session.flush()
                cache[cat.nombre] = cat
            item.categoria_id = cat.id

        db.session.commit()
    except Exception:
        db.session.rollback()


def _migrar_estados_cambio():
    insp = inspect(db.engine)
    if 'estados_cambio' not in insp.get_table_names():
        with db.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE estados_cambio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reserva_id INTEGER NOT NULL,
                    estado_anterior_id INTEGER NULL,
                    estado_nuevo_id INTEGER NOT NULL,
                    usuario_id INTEGER NULL,
                    usuario_email VARCHAR(120) NULL,
                    motivo TEXT NULL,
                    ip VARCHAR(45) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reserva_id) REFERENCES reservas(id),
                    FOREIGN KEY (estado_anterior_id) REFERENCES estados_reserva(id),
                    FOREIGN KEY (estado_nuevo_id) REFERENCES estados_reserva(id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """))
            try:
                conn.execute(text(
                    "CREATE INDEX idx_estados_cambio_reserva ON estados_cambio(reserva_id)"
                ))
            except Exception:
                pass
