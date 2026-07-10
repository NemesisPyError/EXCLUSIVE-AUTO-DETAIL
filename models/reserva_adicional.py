from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint


class ReservaAdicional(db.Model):
    __tablename__ = 'reserva_adicionales'
    __table_args__ = (
        UniqueConstraint('reserva_id', 'servicio_id', name='uq_reserva_adicional'),
        CheckConstraint('precio_aplicado >= 0', name='ck_precio_adicional'),
        CheckConstraint('tiempo_aplicado_min > 0', name='ck_tiempo_adicional'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(
        ForeignKey('reservas.id'), nullable=False, index=True
    )
    servicio_id: Mapped[int] = mapped_column(
        ForeignKey('servicios.id'), nullable=False
    )
    precio_aplicado: Mapped[int] = mapped_column(db.Integer, nullable=False)
    tiempo_aplicado_min: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    reserva: Mapped['Reserva'] = relationship(back_populates='adicionales')
    servicio: Mapped['Servicio'] = relationship(back_populates='reserva_adicionales')

    def __repr__(self):
        return f'<ReservaAdicional r={self.reserva_id} s={self.servicio_id}>'
