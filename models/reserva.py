from extensions import db
from datetime import datetime, timedelta


class Reserva(db.Model):
    __tablename__ = 'reservas'

    id                      = db.Column(db.Integer, primary_key=True)
    cliente_id              = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    estado_id               = db.Column(db.Integer, db.ForeignKey('estados_reserva.id'), nullable=False)
    fecha                   = db.Column(db.Date, nullable=False)
    hora_inicio             = db.Column(db.Time, nullable=False)
    duracion_total_min      = db.Column(db.Integer, nullable=True)
    hora_fin                = db.Column(db.Time, nullable=True)
    fecha_fin               = db.Column(db.Date, nullable=True)
    dias_bloqueo            = db.Column(db.Integer, nullable=True)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    observaciones           = db.Column(db.Text, nullable=True)

    categoria_servicio_id   = db.Column(
        db.Integer, db.ForeignKey('categorias_servicio.id'), nullable=True
    )

    tipo_lavado_id          = db.Column(
        db.Integer, db.ForeignKey('tipos_lavado.id'), nullable=True
    )

    subtipo_lavado_id       = db.Column(
        db.Integer, db.ForeignKey('subtipos_lavado.id'), nullable=True
    )

    tipo_detallado_id       = db.Column(
        db.Integer, db.ForeignKey('tipos_detallado.id'), nullable=True
    )

    requiere_inspeccion     = db.Column(db.Boolean, default=False)
    precio_estimado         = db.Column(db.Numeric(10, 2), nullable=True)
    precio_final            = db.Column(db.Numeric(10, 2), nullable=True)

    asignado_a_id           = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    confirmacion_token      = db.Column(db.String(128), nullable=True, unique=True)

    categoria_servicio = db.relationship('CategoriaServicio', backref='reservas')
    tipo_lavado        = db.relationship('TipoLavado', backref='reservas')
    subtipo_lavado     = db.relationship('SubTipoLavado', backref='reservas')
    tipo_detallado     = db.relationship('TipoDetallado', backref='reservas')
    asignado_a         = db.relationship('Usuario', backref='reservas_asignadas')

    vehiculos = db.relationship('Vehiculo', backref='reserva', lazy='dynamic')
    servicios = db.relationship('ReservaServicio', backref='reserva', lazy='dynamic')
    factores_tiempo = db.relationship('ReservaFactorTiempo', backref='reserva', lazy='dynamic',
                                       cascade='all, delete-orphan')

    @property
    def servicios_nombres(self):
        return [rs.servicio.nombre for rs in self.servicios.all()]

    @property
    def hora_fin_calculada(self):
        if self.hora_fin:
            return self.hora_fin
        if self.duracion_total_min and self.hora_inicio:
            base = datetime.combine(datetime.today(), self.hora_inicio)
            fin = base + timedelta(minutes=self.duracion_total_min)
            return fin.time()
        return None

    @property
    def factores_nombres(self):
        return [rf.factor.nombre for rf in self.factores_tiempo if rf.factor]

    def __repr__(self):
        return f'<Reserva #{self.id} - {self.fecha} {self.hora_inicio}>'


class ReservaServicio(db.Model):
    __tablename__ = 'reserva_servicios'

    id          = db.Column(db.Integer, primary_key=True)
    reserva_id  = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)

    servicio = db.relationship('Servicio', backref='reserva_servicios')
