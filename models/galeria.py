from extensions import db
from datetime import datetime


class Galeria(db.Model):
    __tablename__ = 'galeria'

    id            = db.Column(db.Integer, primary_key=True)
    titulo        = db.Column(db.String(120), nullable=False)
    descripcion   = db.Column(db.Text, nullable=True)
    url_imagen    = db.Column(db.String(255), nullable=False)
    url_thumb     = db.Column(db.String(255), nullable=True)
    tipo          = db.Column(db.String(120), nullable=False, default='')   # legacy: nombre de categoría
    categoria_id  = db.Column(db.Integer, db.ForeignKey('galeria_categoria.id', ondelete='CASCADE'), nullable=True, index=True)
    activo        = db.Column(db.Boolean, default=True)
    orden         = db.Column(db.Integer, nullable=False, default=0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Galeria {self.titulo}>'

