from extensions import db
from datetime import datetime


class Testimonio(db.Model):
    __tablename__ = 'testimonios'

    id                  = db.Column(db.Integer, primary_key=True)
    cliente_id          = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    comentario          = db.Column(db.Text, nullable=False)
    valoracion          = db.Column(db.Integer, nullable=False)
    vehiculo_descripcion = db.Column(db.String(100), nullable=True)
    activo              = db.Column(db.Boolean, default=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('Cliente', backref='testimonios')

    def __repr__(self):
        return f'<Testimonio #{self.id} — {self.valoracion}/5>'
