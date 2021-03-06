from contextlib import closing

import typer
from sqlalchemy.orm import Session
from typer.colors import CYAN, RED

from rankr.crud import country_process, institution_process
from rankr.db_models import Country, SessionLocal


def db_grid():
    """Populates the database with country & GRID data."""
    try:
        db: Session
        typer.secho("Processing countries...", fg=CYAN)
        with closing(SessionLocal()) as db:
            db.add_all(country_process())
            db.commit()

        typer.secho("Processing institutions...", fg=CYAN)
        with closing(SessionLocal()) as db:
            countries = {c.country: c for c in db.query(Country).all()}
            db.add_all(institution_process(countries=countries))
            typer.secho(
                "Committing results to the DB. This can take several minutes.",
                fg=CYAN,
            )
            db.commit()
    except Exception as exc:
        typer.secho("Error populating the database:", fg=RED)
        typer.secho(str(exc), fg=CYAN)
        raise typer.Abort()
