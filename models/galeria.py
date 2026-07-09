from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional


class Galeria(db.Model):
    __tablename__ = 'galeria'

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey('galeria_categorias.id'), nullable=False
    )
    titulo: Mapped[Optional[str]] = mapped_column(db.String(100), nullable=True)
    url_imagen: Mapped[str] = mapped_column(db.String(255), nullable=False)
    url_thumb: Mapped[str] = mapped_column(db.String(255), nullable=False)
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

    categoria: Mapped['GaleriaCategoria'] = relationship(back_populates='imagenes')

    def __repr__(self):
        return f'<Galeria {self.titulo or self.id}>'
