from extensions import db
from datetime import datetime


class GaleriaCategoria(db.Model):
    __tablename__ = 'galeria_categoria'

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(120), nullable=False, unique=True)
    orden      = db.Column(db.Integer, nullable=False, default=0)
    activo     = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    imagenes = db.relationship(
        'Galeria',
        backref='categoria',
        cascade='all, delete-orphan',
        lazy=True,
    )

    def __repr__(self):
        return f'<GaleriaCategoria {self.nombre}>'
