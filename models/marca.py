from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class Marca(db.Model):
    __tablename__ = 'marcas'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    pais_origen: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )

    modelos: Mapped[List['ModeloVehiculo']] = relationship(back_populates='marca')
    vehiculos: Mapped[List['Vehiculo']] = relationship(back_populates='marca')
    solicitudes_resueltas: Mapped[List['SolicitudCatalogo']] = relationship(
        back_populates='marca', foreign_keys='SolicitudCatalogo.marca_id'
    )

    def __repr__(self):
        return f'<Marca {self.nombre}>'
