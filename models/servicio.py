from extensions import db
from datetime import datetime
import enum


class CategoriaServicioEnum(str, enum.Enum):
    LAVADO_VEHICULO     = 'lavado_vehiculo'
    LAVADO_MOTO         = 'lavado_moto'
    TRATAMIENTO_PINTURA = 'tratamiento_pintura'
    RETIRO_ENTREGA      = 'retiro_entrega'


class Servicio(db.Model):
    __tablename__ = 'servicios'

    id                  = db.Column(db.Integer, primary_key=True)

    nombre              = db.Column(db.String(120), nullable=False)
    descripcion         = db.Column(db.Text, nullable=True)

    categoria           = db.Column(db.String(30), nullable=False)
    categoria_servicio_id = db.Column(
        db.Integer, db.ForeignKey('categorias_servicio.id'), nullable=True
    )

    precio              = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tiempo_estimado_min = db.Column(db.Integer, nullable=False, default=0)
    activo              = db.Column(db.Boolean, default=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    categoria_rel = db.relationship('CategoriaServicio', backref='servicios')

    @property
    def tiempo_estimado_formateado(self):
        horas = self.tiempo_estimado_min // 60
        minutos = self.tiempo_estimado_min % 60
        if horas and minutos:
            return f'{horas}h {minutos}min'
        if horas:
            return f'{horas}h'
        return f'{minutos}min'

    def __repr__(self):
        return f'<Servicio {self.nombre}>'
