import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _root)

from app import create_app
from extensions import db

config = context.config

if config.config_file_name is not None:
    cfg_path = config.config_file_name
    if not os.path.isabs(cfg_path):
        cfg_path = os.path.join(_root, cfg_path)
    if os.path.exists(cfg_path):
        fileConfig(cfg_path)

flask_app = create_app(os.getenv('FLASK_ENV', 'development'))
config.set_main_option('sqlalchemy.url', flask_app.config['SQLALCHEMY_DATABASE_URI'])

target_metadata = db.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
