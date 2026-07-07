from extensions import db
from datetime import datetime


class CategoriaServicio(db.Model):
    __tablename__ = 'categorias_servicio'

    id                    = db.Column(db.Integer, primary_key=True)
    nombre                = db.Column(db.String(60), nullable=False, unique=True)
    slug                  = db.Column(db.String(60), nullable=False, unique=True)
    descripcion           = db.Column(db.Text, nullable=True)
    icono                 = db.Column(db.String(60), nullable=True)
    orden                 = db.Column(db.Integer, nullable=False, default=0)
    usa_nivel_suciedad    = db.Column(db.Boolean, default=False)
    permite_multidias     = db.Column(db.Boolean, default=False)
    tiene_subtipos        = db.Column(db.Boolean, default=False)
    activo                = db.Column(db.Boolean, default=True)
    created_at            = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CategoriaServicio {self.nombre}>'
