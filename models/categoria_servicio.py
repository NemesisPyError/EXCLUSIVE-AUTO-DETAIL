from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


class CategoriaServicio(db.Model):
    __tablename__ = 'categorias_servicio'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(40), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(db.String(40), unique=True, nullable=False)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)

    servicios: Mapped[List['Servicio']] = relationship(back_populates='categoria')

    def __repr__(self):
        return f'<CategoriaServicio {self.nombre}>'
