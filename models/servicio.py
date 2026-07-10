from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from typing import Optional, List


class Servicio(db.Model):
    __tablename__ = 'servicios'
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('base', 'adicional', 'paquete')",
            name='ck_servicios_tipo',
        ),
        CheckConstraint(
            "requiere_varios_dias = FALSE OR dias_bloqueo IS NOT NULL",
            name='ck_servicios_dias',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_servicio_id: Mapped[int] = mapped_column(
        ForeignKey('categorias_servicio.id'), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(db.String(80), nullable=False)
    slug: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    tipo: Mapped[str] = mapped_column(db.String(15), nullable=False)
    requiere_inspeccion_previa: Mapped[bool] = mapped_column(
        db.Boolean, default=False, nullable=False
    )
    requiere_varios_dias: Mapped[bool] = mapped_column(
        db.Boolean, default=False, nullable=False
    )
    dias_bloqueo: Mapped[Optional[int]] = mapped_column(db.SmallInteger, nullable=True)
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

    categoria: Mapped['CategoriaServicio'] = relationship(back_populates='servicios')
    precios: Mapped[List['PrecioServicio']] = relationship(back_populates='servicio')
    reservas: Mapped[List['Reserva']] = relationship(back_populates='servicio')
    reserva_adicionales: Mapped[List['ReservaAdicional']] = relationship(back_populates='servicio')

    def __repr__(self):
        return f'<Servicio {self.nombre} ({self.tipo})>'
