from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional


class Configuracion(db.Model):
    __tablename__ = 'configuracion'

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(db.String(60), unique=True, nullable=False)
    valor: Mapped[str] = mapped_column(db.Text, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(db.String(200), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f'<Configuracion {self.clave}>'
