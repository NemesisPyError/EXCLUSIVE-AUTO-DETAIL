from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, PrimaryKeyConstraint


class ServicioTipoVehiculo(db.Model):
    __tablename__ = 'servicio_tipo_vehiculo'
    __table_args__ = (
        PrimaryKeyConstraint('servicio_id', 'tipo_vehiculo_id'),
    )

    servicio_id: Mapped[int] = mapped_column(
        ForeignKey('servicios.id'), nullable=False
    )
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey('tipos_vehiculo.id'), nullable=False
    )

    def __repr__(self):
        return f'<ServicioTipoVehiculo s={self.servicio_id} tv={self.tipo_vehiculo_id}>'
