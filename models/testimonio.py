from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from typing import Optional


class Testimonio(db.Model):
    __tablename__ = 'testimonios'
    __table_args__ = (
        CheckConstraint(
            'valoracion BETWEEN 1 AND 5',
            name='ck_testimonios_valoracion',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('clientes.id'), nullable=True
    )
    comentario: Mapped[str] = mapped_column(db.Text, nullable=False)
    valoracion: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    vehiculo_descripcion: Mapped[Optional[str]] = mapped_column(db.String(100), nullable=True)
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

    cliente: Mapped[Optional['Cliente']] = relationship(back_populates='testimonios')

    def __repr__(self):
        return f'<Testimonio {self.id} {self.valoracion}/5>'
