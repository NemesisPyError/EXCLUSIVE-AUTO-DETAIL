from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


class GaleriaCategoria(db.Model):
    __tablename__ = 'galeria_categorias'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(60), unique=True, nullable=False)
    orden: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    imagenes: Mapped[List['Galeria']] = relationship(
        back_populates='categoria', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<GaleriaCategoria {self.nombre}>'
