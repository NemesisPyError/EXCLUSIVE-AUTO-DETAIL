from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from typing import Optional, List


class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    __table_args__ = (
        CheckConstraint(
            "(marca_id IS NOT NULL AND modelo_id IS NOT NULL) OR "
            "(marca_texto IS NOT NULL AND modelo_texto IS NOT NULL)",
            name='ck_vehiculos_catalogado',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey('clientes.id'), nullable=False, index=True
    )
    marca_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('marcas.id'), nullable=True
    )
    modelo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('modelos_vehiculo.id'), nullable=True, index=True
    )
    marca_texto: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)
    modelo_texto: Mapped[Optional[str]] = mapped_column(db.String(80), nullable=True)
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_vehiculo.id'), nullable=False
    )
    segmento_id: Mapped[int] = mapped_column(
        ForeignKey('segmentos.id'), nullable=False
    )
    anio: Mapped[Optional[int]] = mapped_column(db.SmallInteger, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(db.String(30), nullable=True)
    chapa: Mapped[Optional[str]] = mapped_column(db.String(15), nullable=True)
    combustible: Mapped[Optional[str]] = mapped_column(db.String(20), nullable=True)
    transmision: Mapped[Optional[str]] = mapped_column(db.String(20), nullable=True)
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

    cliente: Mapped['Cliente'] = relationship(back_populates='vehiculos')
    marca: Mapped[Optional['Marca']] = relationship(back_populates='vehiculos')
    modelo: Mapped[Optional['ModeloVehiculo']] = relationship(back_populates='vehiculos')
    tipo_vehiculo: Mapped['TipoVehiculo'] = relationship(back_populates='vehiculos')
    segmento: Mapped['Segmento'] = relationship(back_populates='vehiculos')
    reservas: Mapped[List['Reserva']] = relationship(back_populates='vehiculo')
    solicitudes: Mapped[List['SolicitudCatalogo']] = relationship(back_populates='vehiculo')

    def __repr__(self):
        return f'<Vehiculo {self.id} cliente={self.cliente_id}>'
