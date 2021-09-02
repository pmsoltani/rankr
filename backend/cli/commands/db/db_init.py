import subprocess

import typer
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy_utils import database_exists, drop_database

from config import dbc
from rankr import db_models as d


config = Config()
config.set_main_option("script_location", str(dbc.MIGRATIONS_DIR))
script = ScriptDirectory.from_config(config)

head_revision = script.get_current_head()


def db_init(drop: bool = typer.Option(False, help="Drop the database first?")):
    """Creates the database and its tables.

    Args:
        drop (bool, optional): Drops the database before creating it.
        Defaults to False.

    Raises:
        typer.Abort: If there is a problem with creating the database
    """
    if drop and database_exists(d.engine.url):
        drop_database(d.engine.url)
        typer.secho("Dropped the database!", fg=typer.colors.CYAN)

    try:
        if not head_revision:
            # There are no migration revisions present
            subprocess.check_call(
                args="alembic revision --autogenerate -m 'First Migration'",
                shell=True,
            )
        subprocess.check_call(args="alembic upgrade head", shell=True)
        typer.secho(
            "Successfully migrated the database to its head!",
            fg=typer.colors.GREEN,
        )
    except subprocess.CalledProcessError as exc:
        typer.secho(
            f"Error migrating the database: {type(exc)}", fg=typer.colors.RED
        )
        typer.secho(str(exc), fg=typer.colors.CYAN)
        raise typer.Abort()
