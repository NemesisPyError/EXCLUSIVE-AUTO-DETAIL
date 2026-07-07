from extensions import db
from datetime import datetime


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(80), nullable=False)
    apellido      = db.Column(db.String(80), nullable=False)
    cedula        = db.Column(db.String(20), nullable=False)
    telefono      = db.Column(db.String(20), nullable=False)
    email         = db.Column(db.String(150), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    reservas = db.relationship('Reserva', backref='cliente', lazy='dynamic')

    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellido}>'
