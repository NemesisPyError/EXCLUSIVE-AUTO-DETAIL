from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from typing import Optional


class SolicitudCatalogo(db.Model):
    __tablename__ = 'solicitudes_catalogo'
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'aprobada', 'rechazada')",
            name='ck_solicitudes_estado',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marca_texto: Mapped[str] = mapped_column(db.String(50), nullable=False)
    modelo_texto: Mapped[str] = mapped_column(db.String(80), nullable=False)
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_vehiculo.id'), nullable=False
    )
    segmento_id: Mapped[int] = mapped_column(
        ForeignKey('segmentos.id'), nullable=False
    )
    cliente_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('clientes.id'), nullable=True
    )
    vehiculo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('vehiculos.id'), nullable=True
    )
    marca_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('marcas.id'), nullable=True
    )
    modelo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('modelos_vehiculo.id'), nullable=True
    )
    usuario_aprobador_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('usuarios.id'), nullable=True
    )
    estado: Mapped[str] = mapped_column(
        db.String(15), default='pendiente', nullable=False, index=True
    )
    observaciones: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tipo_vehiculo: Mapped['TipoVehiculo'] = relationship(back_populates='solicitudes')
    segmento: Mapped['Segmento'] = relationship(back_populates='solicitudes')
    cliente: Mapped[Optional['Cliente']] = relationship(back_populates='solicitudes')
    vehiculo: Mapped[Optional['Vehiculo']] = relationship(back_populates='solicitudes')
    marca: Mapped[Optional['Marca']] = relationship(
        back_populates='solicitudes_resueltas', foreign_keys=[marca_id]
    )
    usuario_aprobador: Mapped[Optional['Usuario']] = relationship(
        back_populates='solicitudes_aprobadas', foreign_keys=[usuario_aprobador_id]
    )

    def __repr__(self):
        return f'<SolicitudCatalogo {self.id} {self.marca_texto} {self.modelo_texto} ({self.estado})>'
