import typer
from sqlalchemy_utils import create_database, database_exists, drop_database
from typer.colors import CYAN, GREEN, RED

from config import dbc
from rankr import db_models as d


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
        typer.secho("Dropped the database!", fg=CYAN)

    try:
        create_database(d.engine.url, encoding=dbc.DB_ENCODING)

        d.Base.metadata.create_all(d.engine)
        typer.secho("Successfully created the database!", fg=GREEN)
    except Exception as exc:
        typer.secho("Error creating the database:", fg=RED)
        typer.secho(str(exc), fg=CYAN)
        raise typer.Abort()
