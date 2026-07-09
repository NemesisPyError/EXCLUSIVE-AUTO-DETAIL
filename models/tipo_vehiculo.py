from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class TipoVehiculo(db.Model):
    __tablename__ = 'tipos_vehiculo'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    icono: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)

    modelos: Mapped[List['ModeloVehiculo']] = relationship(back_populates='tipo_vehiculo')
    vehiculos: Mapped[List['Vehiculo']] = relationship(back_populates='tipo_vehiculo')
    precios: Mapped[List['PrecioServicio']] = relationship(back_populates='tipo_vehiculo')
    solicitudes: Mapped[List['SolicitudCatalogo']] = relationship(back_populates='tipo_vehiculo')

    def __repr__(self):
        return f'<TipoVehiculo {self.nombre}>'
