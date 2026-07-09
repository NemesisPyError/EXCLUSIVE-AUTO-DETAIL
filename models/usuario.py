from datetime import datetime, timedelta, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint
from typing import Optional, List
import secrets
import bcrypt


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = (
        CheckConstraint(
            "rol IN ('admin', 'empleado')",
            name='ck_usuarios_rol',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(db.String(60), nullable=False)
    apellido: Mapped[str] = mapped_column(db.String(60), nullable=False)
    rol: Mapped[str] = mapped_column(db.String(15), nullable=False)
    activo: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False, index=True)
    login_attempts: Mapped[int] = mapped_column(db.SmallInteger, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )
    session_version: Mapped[int] = mapped_column(db.Integer, default=1, nullable=False)
    reset_token: Mapped[Optional[str]] = mapped_column(
        db.String(64), unique=True, nullable=True
    )
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True), nullable=True
    )

    reservas_asignadas: Mapped[List['Reserva']] = relationship(
        back_populates='usuario_asignado', foreign_keys='Reserva.usuario_asignado_id'
    )
    solicitudes_aprobadas: Mapped[List['SolicitudCatalogo']] = relationship(
        back_populates='usuario_aprobador', foreign_keys='SolicitudCatalogo.usuario_aprobador_id'
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'), self.password_hash.encode('utf-8')
        )

    MAX_LOGIN_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 15
    RESET_TOKEN_EXPIRY_MINUTES = 15

    @property
    def is_locked(self) -> bool:
        if not self.locked_until:
            return False
        return self.locked_until > datetime.now(timezone.utc)

    def record_failed_attempt(self) -> None:
        self.login_attempts = (self.login_attempts or 0) + 1
        if self.login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.LOCK_DURATION_MINUTES)

    def unlock_if_expired(self) -> None:
        if self.locked_until and self.locked_until <= datetime.now(timezone.utc):
            self.locked_until = None
            self.login_attempts = 0

    def reset_login_attempts(self) -> None:
        self.login_attempts = 0
        self.locked_until = None

    def generate_reset_token(self) -> None:
        self.reset_token = secrets.token_hex(32)
        self.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=self.RESET_TOKEN_EXPIRY_MINUTES)

    def clear_reset_token(self) -> None:
        self.reset_token = None
        self.reset_token_expires = None

    def increment_session_version(self) -> None:
        self.session_version = (self.session_version or 1) + 1

    def is_authenticated(self) -> bool:
        return True

    def is_active(self) -> bool:
        return self.activo

    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.id)

    def __repr__(self):
        return f'<Usuario {self.email}>'
