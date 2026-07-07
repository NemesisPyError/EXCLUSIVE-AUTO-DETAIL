from extensions import db
from datetime import datetime


class SubTipoLavado(db.Model):
    __tablename__ = 'subtipos_lavado'

    id              = db.Column(db.Integer, primary_key=True)
    tipo_lavado_id  = db.Column(db.Integer, db.ForeignKey('tipos_lavado.id'), nullable=False)
    nombre          = db.Column(db.String(30), nullable=False)
    slug            = db.Column(db.String(30), nullable=False)
    descripcion     = db.Column(db.Text, nullable=True)
    orden           = db.Column(db.Integer, nullable=False, default=0)
    activo          = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SubTipoLavado {self.nombre}>'
