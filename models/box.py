from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List


class Box(db.Model):
    __tablename__ = 'boxes'

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_box_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_box.id'), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    activo: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False, index=True)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tipo_box: Mapped['TipoBox'] = relationship(back_populates='boxes')
    reservas: Mapped[List['Reserva']] = relationship(back_populates='box')

    def __repr__(self):
        return f'<Box {self.nombre}>'
