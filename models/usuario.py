from extensions import db
from flask_login import UserMixin
import bcrypt
import secrets
from datetime import datetime, timedelta, UTC


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol           = db.Column(db.String(20), nullable=False, default='empleado')
    activo        = db.Column(db.Boolean, default=True)
    login_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until   = db.Column(db.DateTime, nullable=True)
    session_version = db.Column(db.Integer, nullable=False, default=0)
    reset_token     = db.Column(db.String(128), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    RESET_TOKEN_MINUTES = 15

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), salt
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.now(UTC):
            return True
        return False

    def unlock_if_expired(self):
        if self.locked_until and self.locked_until <= datetime.now(UTC):
            self.login_attempts = 0
            self.locked_until = None

    def record_failed_attempt(self):
        self.login_attempts = (self.login_attempts or 0) + 1
        if self.login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            self.locked_until = datetime.now(UTC) + timedelta(minutes=self.LOCKOUT_MINUTES)
            self.increment_session_version()

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None

    def increment_session_version(self):
        self.session_version = (self.session_version or 0) + 1

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=self.RESET_TOKEN_MINUTES)

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    def __repr__(self):
        return f'<Usuario {self.email}>'
