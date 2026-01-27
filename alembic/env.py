import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# 1. On charge le .env
load_dotenv()

# 2. On configure le chemin Python (Avant les imports du projet !)
sys.path.append(os.getcwd())

# 3. On importe nos fichiers (avec l'exception pour le linter)
from app.db.database import Base  # noqa: E402


# 4. On définit les métadonnées
target_metadata = Base.metadata

# 5. Configuration Alembic
config = context.config

# 6. On écrase l'URL par défaut avec celle sécurisée du .env
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# 7. On charge le fichier de configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 8. Fonction pour les migrations offline
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# 9. Fonction pour les migrations online
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# 10. On lance les migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
