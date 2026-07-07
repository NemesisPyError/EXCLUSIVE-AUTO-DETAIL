from extensions import db
from datetime import datetime


class ReglaPrecio(db.Model):
    __tablename__ = 'reglas_precio'

    id                      = db.Column(db.Integer, primary_key=True)
    categoria_servicio_id   = db.Column(db.Integer, db.ForeignKey('categorias_servicio.id'), nullable=False)
    tipo_vehiculo_id        = db.Column(db.Integer, db.ForeignKey('tipos_vehiculo.id'), nullable=False)
    tipo_lavado_id          = db.Column(db.Integer, db.ForeignKey('tipos_lavado.id'), nullable=True)
    subtipo_lavado_id       = db.Column(db.Integer, db.ForeignKey('subtipos_lavado.id'), nullable=True)
    tipo_detallado_id       = db.Column(db.Integer, db.ForeignKey('tipos_detallado.id'), nullable=True)
    servicio_id             = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=True)
    precio_fijo             = db.Column(db.Numeric(10, 2), nullable=True)
    precio_estimado         = db.Column(db.Numeric(10, 2), nullable=True)
    es_precio_estimado      = db.Column(db.Boolean, default=False)
    tiempo_estimado_min     = db.Column(db.Integer, nullable=False, default=0)
    dias_bloqueo            = db.Column(db.Integer, nullable=False, default=0)
    descripcion_publica     = db.Column(db.Text, nullable=True)
    nota_inspeccion         = db.Column(db.Text, nullable=True)
    activo                  = db.Column(db.Boolean, default=True)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)

    categoria_servicio = db.relationship('CategoriaServicio', backref='reglas_precio')
    tipo_vehiculo      = db.relationship('TipoVehiculo', backref='reglas_precio')
    tipo_lavado        = db.relationship('TipoLavado', backref='reglas_precio')
    subtipo_lavado     = db.relationship('SubTipoLavado', backref='reglas_precio')
    tipo_detallado     = db.relationship('TipoDetallado', backref='reglas_precio')
    servicio           = db.relationship('Servicio', backref='reglas_precio')

    __table_args__ = (
        db.Index('idx_reglas_combinacion',
                 'categoria_servicio_id', 'tipo_vehiculo_id',
                 'tipo_lavado_id', 'subtipo_lavado_id',
                 'tipo_detallado_id', 'servicio_id'),
    )

    def __repr__(self):
        return (f'<ReglaPrecio cat={self.categoria_servicio_id} '
                f'veh={self.tipo_vehiculo_id}>')
