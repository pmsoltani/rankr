from pathlib import Path

import typer

from rankr import db_models as d


def db_init(drop: bool = typer.Option(False, help="Drop the database first?")):
    """Creates the SQLite database file and all of its tables.

    Args:
        drop (bool, optional): Deletes the database file before creating it.
        Defaults to False.
    """
    if drop:
        db_path = d.engine.url.database
        if db_path:
            # Remove the main db file plus any WAL sidecar files.
            for suffix in ("", "-wal", "-shm"):
                file = Path(f"{db_path}{suffix}")
                if file.exists():
                    file.unlink()
            typer.secho("Dropped the database!", fg=typer.colors.CYAN)

    d.Base.metadata.create_all(d.engine)
    typer.secho("Created the database and all tables!", fg=typer.colors.GREEN)
