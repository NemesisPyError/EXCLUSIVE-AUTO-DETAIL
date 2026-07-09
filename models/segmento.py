from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class Segmento(db.Model):
    __tablename__ = 'segmentos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)

    modelos: Mapped[List['ModeloVehiculo']] = relationship(back_populates='segmento')
    vehiculos: Mapped[List['Vehiculo']] = relationship(back_populates='segmento')
    precios: Mapped[List['PrecioServicio']] = relationship(back_populates='segmento')
    solicitudes: Mapped[List['SolicitudCatalogo']] = relationship(back_populates='segmento')

    def __repr__(self):
        return f'<Segmento {self.nombre}>'
