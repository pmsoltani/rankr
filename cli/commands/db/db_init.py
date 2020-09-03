import typer
from sqlalchemy_utils import create_database, database_exists, drop_database
from typer.colors import CYAN, GREEN, RED

from config import dbc
from rankr.db_models import Base, engine


def db_init(drop: bool = typer.Option(False, help="Drop the database first?")):
    """Creates the database and its tables.

    Args:
        drop (bool, optional): Drops the database before creating it.
        Defaults to False.

    Raises:
        typer.Abort: If there is a problem with creating the database
    """
    if drop and database_exists(engine.url):
        drop_database(engine.url)
        typer.secho("Dropped the database!", fg=CYAN)

    try:
        encoding = "utf8mb4" if dbc.DIALECT == "mysql" else "utf8"
        create_database(engine.url, encoding=encoding)

        Base.metadata.create_all(engine)
        typer.secho("Successfully created the database!", fg=GREEN)
    except Exception as exc:
        typer.secho("Error creating the database:", fg=RED)
        typer.secho(str(exc), fg=CYAN)
        raise typer.Abort()
