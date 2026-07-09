from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


class EstadoReserva(db.Model):
    __tablename__ = 'estados_reserva'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    color_badge: Mapped[str] = mapped_column(db.String(7), nullable=False)
    orden: Mapped[int] = mapped_column(db.SmallInteger, unique=True, nullable=False)
    es_terminal: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    es_cancelacion: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)

    reservas: Mapped[List['Reserva']] = relationship(back_populates='estado')

    def __repr__(self):
        return f'<EstadoReserva {self.nombre}>'
