from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from typing import Optional


class FotografiaReserva(db.Model):
    __tablename__ = 'fotografias_reserva'
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('antes', 'despues')",
            name='ck_fotografias_tipo',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(
        ForeignKey('reservas.id'), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(db.String(10), nullable=False, index=True)
    url_imagen: Mapped[str] = mapped_column(db.String(255), nullable=False)
    url_thumb: Mapped[str] = mapped_column(db.String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.String(200), nullable=True)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id'), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    reserva: Mapped['Reserva'] = relationship(back_populates='fotografias')

    def __repr__(self):
        return f'<FotografiaReserva r={self.reserva_id} tipo={self.tipo}>'
