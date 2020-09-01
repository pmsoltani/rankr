import typer
from sqlalchemy_utils import create_database, database_exists, drop_database

from config import DBConfig
from rankr.db_models import Base, engine


def db_init(force: bool = False):
    if force and database_exists(engine.url):
        drop_database(engine.url)
        typer.secho("Dropped the database!", fg="cyan")

    try:
        if not database_exists(engine.url):
            encoding = "utf8mb4" if DBConfig.DIALECT == "mysql" else "utf8"
            create_database(engine.url, encoding=encoding)

        Base.metadata.create_all(engine)
        typer.secho("Successfully created the database!", fg="green")
    except Exception as exc:
        typer.secho("Error creating the database:", fg="red")
        typer.secho(str(exc))
        raise typer.Abort()
