# Standard library
import importlib
import pkgutil
from collections.abc import Iterable
from datetime import datetime
from logging.config import fileConfig

# Third party
from alembic import context
from alembic.operations import MigrationScript
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, pool

# First party
from project_name.app import features
from project_name.app.core.config import settings
from project_name.app.database.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

database_url = str(settings.db.url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _import_feature_models() -> None:
    prefix = f"{features.__name__}."
    for module in pkgutil.walk_packages(features.__path__, prefix):
        if module.name.endswith(".models"):
            importlib.import_module(module.name)


_import_feature_models()
target_metadata = Base.metadata


def _revision_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def process_revision_directives(
    context: MigrationContext,
    revision: str | Iterable[str | None] | Iterable[str],
    directives: list[MigrationScript],
) -> None:
    """Use a timestamp revision id instead of a random hash."""
    del context, revision
    if directives:
        directives[0].rev_id = _revision_id()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
