from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class TipoBox(db.Model):
    __tablename__ = 'tipos_box'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)

    boxes: Mapped[List['Box']] = relationship(back_populates='tipo_box')

    def __repr__(self):
        return f'<TipoBox {self.nombre}>'
