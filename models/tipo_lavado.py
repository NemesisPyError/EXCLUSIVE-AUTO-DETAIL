from extensions import db
from datetime import datetime


class TipoLavado(db.Model):
    __tablename__ = 'tipos_lavado'

    id                    = db.Column(db.Integer, primary_key=True)
    nombre                = db.Column(db.String(30), nullable=False, unique=True)
    slug                  = db.Column(db.String(30), nullable=False, unique=True)
    descripcion           = db.Column(db.Text, nullable=True)
    orden                 = db.Column(db.Integer, nullable=False, default=0)
    es_cerrado            = db.Column(db.Boolean, default=False)
    requiere_inspeccion   = db.Column(db.Boolean, default=False)
    activo                = db.Column(db.Boolean, default=True)
    created_at            = db.Column(db.DateTime, default=datetime.utcnow)

    subtipos = db.relationship('SubTipoLavado', backref='tipo_lavado', lazy='dynamic',
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TipoLavado {self.nombre}>'
