from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection

from alembic import context

from app.infrastructure.database import Base
import app.identity.infrastructure.orm_models  # noqa: F401
import app.clients.infrastructure.orm_models  # noqa: F401
import app.inventory.infrastructure.orm_models  # noqa: F401
import app.quotes.infrastructure.orm_models  # noqa: F401
import app.finance.infrastructure.orm_models  # noqa: F401
import app.commissions.infrastructure.orm_models  # noqa: F401
import app.audit.infrastructure.orm_models  # noqa: F401
import app.prospecting.infrastructure.orm_models  # noqa: F401
import app.pos.infrastructure.orm_models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    import os
    return os.environ.get("DATABASE_URL_SYNC", config.get_main_option("sqlalchemy.url", ""))


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        cfg, prefix="sqlalchemy.", poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
