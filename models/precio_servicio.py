from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint


class PrecioServicio(db.Model):
    __tablename__ = 'precios_servicio'
    __table_args__ = (
        UniqueConstraint(
            'servicio_id', 'tipo_vehiculo_id', 'segmento_id', 'nivel_suciedad_id',
            name='uq_precio_combinacion',
        ),
        CheckConstraint('precio >= 0', name='ck_precio_positivo'),
        CheckConstraint('duracion_minutos > 0', name='ck_duracion_positiva'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    servicio_id: Mapped[int] = mapped_column(
        ForeignKey('servicios.id'), nullable=False, index=True
    )
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_vehiculo.id'), nullable=False
    )
    segmento_id: Mapped[int] = mapped_column(
        ForeignKey('segmentos.id'), nullable=False
    )
    nivel_suciedad_id: Mapped[int] = mapped_column(
        ForeignKey('niveles_suciedad.id'), nullable=False
    )
    precio: Mapped[int] = mapped_column(db.Integer, nullable=False)
    duracion_minutos: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    servicio: Mapped['Servicio'] = relationship(back_populates='precios')
    tipo_vehiculo: Mapped['TipoVehiculo'] = relationship(back_populates='precios')
    segmento: Mapped['Segmento'] = relationship(back_populates='precios')
    nivel_suciedad: Mapped['NivelSuciedad'] = relationship(back_populates='precios')

    def __repr__(self):
        return (
            f'<PrecioServicio svc={self.servicio_id} '
            f'tv={self.tipo_vehiculo_id} seg={self.segmento_id} '
            f'suc={self.nivel_suciedad_id} Gs{self.precio}>'
        )
