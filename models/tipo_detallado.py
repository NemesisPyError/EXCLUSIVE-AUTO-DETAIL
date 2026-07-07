from extensions import db
from datetime import datetime


class TipoDetallado(db.Model):
    __tablename__ = 'tipos_detallado'

    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(60), nullable=False, unique=True)
    slug            = db.Column(db.String(60), nullable=False, unique=True)
    descripcion     = db.Column(db.Text, nullable=True)
    orden           = db.Column(db.Integer, nullable=False, default=0)
    activo          = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TipoDetallado {self.nombre}>'
