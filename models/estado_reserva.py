from extensions import db


class EstadoReserva(db.Model):
    __tablename__ = 'estados_reserva'

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(60), unique=True, nullable=False)
    color_badge = db.Column(db.String(7), nullable=False, default='#6c757d')
    orden       = db.Column(db.Integer, nullable=False, default=0)

    reservas = db.relationship('Reserva', backref='estado', lazy='dynamic')

    def __repr__(self):
        return f'<EstadoReserva {self.nombre}>'
