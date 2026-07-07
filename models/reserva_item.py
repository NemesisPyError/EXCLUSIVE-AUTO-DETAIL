from extensions import db


class ReservaItem(db.Model):
    __tablename__ = 'reserva_items'

    id                  = db.Column(db.Integer, primary_key=True)
    reserva_id          = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    tipo_item           = db.Column(db.String(30), nullable=False)
    regla_precio_id     = db.Column(db.Integer, db.ForeignKey('reglas_precio.id'), nullable=True)
    servicio_id         = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=True)
    precio_aplicado     = db.Column(db.Numeric(10, 2), nullable=True)
    tiempo_aplicado_min = db.Column(db.Integer, nullable=True)
    descripcion         = db.Column(db.Text, nullable=True)

    reserva       = db.relationship('Reserva', backref='items')
    regla_precio  = db.relationship('ReglaPrecio', backref='reserva_items')
    servicio      = db.relationship('Servicio', backref='reserva_items')

    __table_args__ = (
        db.Index('idx_ri_reserva', 'reserva_id'),
        db.Index('idx_ri_regla_precio', 'regla_precio_id'),
        db.Index('idx_ri_tipo_item', 'tipo_item'),
    )

    def __repr__(self):
        return f'<ReservaItem #{self.id} tipo={self.tipo_item}>'
