from datetime import datetime, date, time, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint, Index
from typing import Optional, List


class Reserva(db.Model):
    __tablename__ = 'reservas'
    __table_args__ = (
        CheckConstraint('duracion_total_min > 0', name='ck_duracion_positiva'),
        Index('ix_reservas_box_fecha_hora', 'box_id', 'fecha', 'hora_inicio'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey('clientes.id'), nullable=False, index=True
    )
    vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('vehiculos.id'), nullable=False
    )
    servicio_id: Mapped[int] = mapped_column(
        ForeignKey('servicios.id'), nullable=False
    )
    estado_reserva_id: Mapped[int] = mapped_column(
        ForeignKey('estados_reserva.id'), nullable=False, index=True
    )
    nivel_suciedad_id: Mapped[int] = mapped_column(
        ForeignKey('niveles_suciedad.id'), nullable=False
    )
    box_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('boxes.id'), nullable=True
    )
    usuario_asignado_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('usuarios.id'), nullable=True, index=True
    )
    fecha: Mapped[date] = mapped_column(db.Date, nullable=False, index=True)
    hora_inicio: Mapped[time] = mapped_column(db.Time, nullable=False)
    duracion_total_min: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)
    fecha_entrega_estimada: Mapped[Optional[date]] = mapped_column(db.Date, nullable=True)
    hora_entrega_estimada: Mapped[Optional[time]] = mapped_column(db.Time, nullable=True)
    precio_estimado_base: Mapped[int] = mapped_column(db.Integer, nullable=False)
    precio_estimado_adicionales: Mapped[int] = mapped_column(
        db.Integer, default=0, nullable=False
    )
    precio_final_base: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    precio_final_adicionales: Mapped[Optional[int]] = mapped_column(
        db.Integer, default=0, nullable=True
    )
    motivo_ajuste_precio: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    confirmacion_token: Mapped[Optional[str]] = mapped_column(
        db.String(64), unique=True, nullable=True
    )
    observaciones_cliente: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    observaciones_internas: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    reagendado_de: Mapped[Optional[int]] = mapped_column(
        ForeignKey('reservas.id'), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey('usuarios.id'), nullable=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey('usuarios.id'), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )

    cliente: Mapped['Cliente'] = relationship(back_populates='reservas')
    vehiculo: Mapped['Vehiculo'] = relationship(back_populates='reservas')
    servicio: Mapped['Servicio'] = relationship(back_populates='reservas')
    estado: Mapped['EstadoReserva'] = relationship(back_populates='reservas')
    nivel_suciedad: Mapped['NivelSuciedad'] = relationship(back_populates='reservas')
    box: Mapped[Optional['Box']] = relationship(back_populates='reservas')
    usuario_asignado: Mapped[Optional['Usuario']] = relationship(
        back_populates='reservas_asignadas', foreign_keys=[usuario_asignado_id]
    )
    adicionales: Mapped[List['ReservaAdicional']] = relationship(back_populates='reserva')
    cambios_estado: Mapped[List['EstadoCambio']] = relationship(back_populates='reserva')
    fotografias: Mapped[List['FotografiaReserva']] = relationship(back_populates='reserva')

    def __repr__(self):
        return f'<Reserva {self.id} {self.fecha} {self.hora_inicio}>'
