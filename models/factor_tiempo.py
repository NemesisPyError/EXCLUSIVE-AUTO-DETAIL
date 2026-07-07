from extensions import db
from datetime import datetime
import enum


class TipoFactor(str, enum.Enum):
    SUCIEDAD = 'suciedad'
    CONDICION = 'condicion'
    GENERICO = 'generico'


class FactorTiempo(db.Model):
    __tablename__ = 'factores_tiempo'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    minutos_adicionales = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FactorTiempo {self.tipo}/{self.nombre} +{self.minutos_adicionales}min>'


class ReservaFactorTiempo(db.Model):
    __tablename__ = 'reserva_factores_tiempo'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    factor_tiempo_id = db.Column(db.Integer, db.ForeignKey('factores_tiempo.id'), nullable=False)

    factor = db.relationship('FactorTiempo', backref='reserva_factores')
