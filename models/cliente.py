from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(60), nullable=False)
    apellido: Mapped[str] = mapped_column(db.String(60), nullable=False)
    telefono: Mapped[str] = mapped_column(
        db.String(20), unique=True, nullable=False, index=True
    )
    cedula: Mapped[Optional[str]] = mapped_column(db.String(20), unique=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(db.String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )

    vehiculos: Mapped[List['Vehiculo']] = relationship(back_populates='cliente')
    reservas: Mapped[List['Reserva']] = relationship(back_populates='cliente')
    testimonios: Mapped[List['Testimonio']] = relationship(back_populates='cliente')
    solicitudes: Mapped[List['SolicitudCatalogo']] = relationship(back_populates='cliente')

    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellido}>'
