from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class NivelSuciedad(db.Model):
    __tablename__ = 'niveles_suciedad'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    orden: Mapped[int] = mapped_column(db.SmallInteger, nullable=False)

    precios: Mapped[List['PrecioServicio']] = relationship(back_populates='nivel_suciedad')
    reservas: Mapped[List['Reserva']] = relationship(back_populates='nivel_suciedad')

    def __repr__(self):
        return f'<NivelSuciedad {self.nombre}>'
