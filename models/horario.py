from datetime import datetime, time as time_type, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint


class Horario(db.Model):
    __tablename__ = 'horarios'
    __table_args__ = (
        CheckConstraint('dia_semana BETWEEN 1 AND 7', name='ck_horarios_dia'),
        CheckConstraint('hora_inicio < hora_fin', name='ck_horarios_horas'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dia_semana: Mapped[int] = mapped_column(
        db.SmallInteger, unique=True, nullable=False
    )
    hora_inicio: Mapped[time_type] = mapped_column(db.Time, nullable=False)
    hora_fin: Mapped[time_type] = mapped_column(db.Time, nullable=False)
    activo: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f'<Horario dia={self.dia_semana} {self.hora_inicio}-{self.hora_fin}>'
