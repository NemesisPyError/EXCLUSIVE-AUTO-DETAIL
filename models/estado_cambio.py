from extensions import db
from datetime import datetime, UTC


class EstadoCambio(db.Model):
    __tablename__ = 'estados_cambio'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False, index=True)
    estado_anterior_id = db.Column(db.Integer, db.ForeignKey('estados_reserva.id'), nullable=True)
    estado_nuevo_id = db.Column(db.Integer, db.ForeignKey('estados_reserva.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    usuario_email = db.Column(db.String(120), nullable=True)
    motivo = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    reserva = db.relationship('Reserva', backref='cambios_estado')
    estado_anterior = db.relationship('EstadoReserva', foreign_keys=[estado_anterior_id])
    estado_nuevo = db.relationship('EstadoReserva', foreign_keys=[estado_nuevo_id])
