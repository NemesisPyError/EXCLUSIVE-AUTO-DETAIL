from extensions import db


class Horario(db.Model):
    __tablename__ = 'horarios'

    id               = db.Column(db.Integer, primary_key=True)
    dia_semana       = db.Column(db.Integer, nullable=False)
    hora_inicio      = db.Column(db.Time, nullable=False)
    hora_fin         = db.Column(db.Time, nullable=False)
    capacidad_maxima = db.Column(db.Integer, nullable=False, default=3)
    activo           = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Horario dia {self.dia_semana} {self.hora_inicio}-{self.hora_fin}>'
