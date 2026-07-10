from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, PrimaryKeyConstraint


class BoxTipoVehiculo(db.Model):
    __tablename__ = 'box_tipo_vehiculo'
    __table_args__ = (
        PrimaryKeyConstraint('tipo_box_id', 'tipo_vehiculo_id'),
    )

    tipo_box_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_box.id'), nullable=False
    )
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_vehiculo.id'), nullable=False
    )

    def __repr__(self):
        return f'<BoxTipoVehiculo tb={self.tipo_box_id} tv={self.tipo_vehiculo_id}>'
