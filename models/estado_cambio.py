from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional


class EstadoCambio(db.Model):
    __tablename__ = 'estados_cambio'

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(
        ForeignKey('reservas.id'), nullable=False, index=True
    )
    estado_anterior_id: Mapped[int] = mapped_column(
        ForeignKey('estados_reserva.id'), nullable=False
    )
    estado_nuevo_id: Mapped[int] = mapped_column(
        ForeignKey('estados_reserva.id'), nullable=False
    )
    usuario_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('usuarios.id'), nullable=True, index=True
    )
    usuario_email: Mapped[str] = mapped_column(db.String(120), nullable=False)
    ip: Mapped[Optional[str]] = mapped_column(db.String(45), nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    reserva: Mapped['Reserva'] = relationship(back_populates='cambios_estado')

    def __repr__(self):
        return f'<EstadoCambio r={self.reserva_id} {self.estado_anterior_id}->{self.estado_nuevo_id}>'
