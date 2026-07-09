from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from typing import Optional, List


class ModeloVehiculo(db.Model):
    __tablename__ = 'modelos_vehiculo'
    __table_args__ = (
        UniqueConstraint('marca_id', 'slug', name='uq_modelos_marca_slug'),
        CheckConstraint(
            'anio_desde IS NULL OR anio_hasta IS NULL OR anio_desde <= anio_hasta',
            name='ck_modelos_anios',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marca_id: Mapped[int] = mapped_column(
        ForeignKey('marcas.id'), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(db.String(80), nullable=False)
    slug: Mapped[str] = mapped_column(db.String(80), nullable=False)
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_vehiculo.id'), nullable=False, index=True
    )
    segmento_id: Mapped[int] = mapped_column(
        ForeignKey('segmentos.id'), nullable=False
    )
    anio_desde: Mapped[Optional[int]] = mapped_column(db.SmallInteger, nullable=True)
    anio_hasta: Mapped[Optional[int]] = mapped_column(db.SmallInteger, nullable=True)
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

    marca: Mapped['Marca'] = relationship(back_populates='modelos')
    tipo_vehiculo: Mapped['TipoVehiculo'] = relationship(back_populates='modelos')
    segmento: Mapped['Segmento'] = relationship(back_populates='modelos')
    vehiculos: Mapped[List['Vehiculo']] = relationship(back_populates='modelo')

    def __repr__(self):
        return f'<ModeloVehiculo {self.marca_id}/{self.nombre}>'
