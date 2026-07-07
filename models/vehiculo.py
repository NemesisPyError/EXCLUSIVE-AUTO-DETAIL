from extensions import db


class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'

    id                = db.Column(db.Integer, primary_key=True)
    reserva_id        = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)

    tipo_vehiculo     = db.Column(db.String(30), nullable=False)
    tipo_vehiculo_id  = db.Column(
        db.Integer, db.ForeignKey('tipos_vehiculo.id'), nullable=True
    )

    marca             = db.Column(db.String(60), nullable=False)
    modelo            = db.Column(db.String(60), nullable=False)
    anio              = db.Column(db.Integer, nullable=True)
    color             = db.Column(db.String(40), nullable=True)

    nivel_suciedad    = db.Column(db.String(10), nullable=True)

    tipo_vehiculo_rel = db.relationship('TipoVehiculo', backref='vehiculos')

    def __repr__(self):
        return f'<Vehiculo {self.marca} {self.modelo}>'
