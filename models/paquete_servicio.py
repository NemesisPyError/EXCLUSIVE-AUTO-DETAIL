from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, CheckConstraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.servicio import Servicio


class PaqueteServicio(db.Model):
    __tablename__ = 'paquete_servicios'
    __table_args__ = (
        PrimaryKeyConstraint('paquete_id', 'servicio_id'),
        CheckConstraint(
            'paquete_id <> servicio_id',
            name='ck_paquete_principal',
        ),
    )

    paquete_id: Mapped[int] = mapped_column(
        ForeignKey('servicios.id'), nullable=False, index=True
    )
    servicio_id: Mapped[int] = mapped_column(
        ForeignKey('servicios.id'), nullable=False
    )
    es_principal: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)

    servicio: Mapped['Servicio'] = relationship(foreign_keys=[servicio_id])

    def __repr__(self):
        return f'<PaqueteServicio pkg={self.paquete_id} svc={self.servicio_id}>'
