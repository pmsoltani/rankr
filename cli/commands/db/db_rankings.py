from pathlib import Path
from typing import List
from sqlalchemy.orm.session import Session

import typer
from typer.colors import CYAN, GREEN, RED

from config import dbc
from rankr.crud import ranking_process
from rankr.db_models import Institution, SessionLocal
from utils import csv_export, csv_size


def db_rankings(commit: bool = typer.Option(True)):
    """Populates the database with ranking data."""
    db: Session = SessionLocal()
    all_institutions: List[Institution] = db.query(Institution).all()
    soup = {}  # Group soup by country for better performance.
    for inst in all_institutions:
        try:
            soup[inst.country.country][inst.soup] = inst.grid_id
        except KeyError:
            soup[inst.country.country] = {inst.soup: inst.grid_id}
    db.close()

    not_mached = []
    fuzz = []
    for ranking_system in list(dbc.RANKINGS["metrics"]):
        # Get the ranking system directory.
        dir_path: Path = dbc.MAIN_DIR / dbc.DATA_DIR / ranking_system
        if not dir_path.exists():
            continue

        # Get all .csv files in the directory.
        files: List[Path] = sorted(
            [f for f in dir_path.iterdir() if f.suffix == ".csv"], reverse=True
        )
        for cnt, file in enumerate(files, start=1):
            typer.secho(
                f"Processing file ({cnt}/{len(files)}): {file.stem}", fg=CYAN
            )
            try:
                db = SessionLocal()
                size = csv_size(file)
                institutions_list, not_mached_list, fuzz_list = ranking_process(
                    db, file, soup
                )
                # TODO: Remove the following unnecessary if-block.
                if len(institutions_list) + len(not_mached_list) != size:
                    raise ValueError("Some institutions may have been lost!")
                not_mached.extend(not_mached_list)
                fuzz.extend(fuzz_list)

                db.add_all(institutions_list)
                db.commit()
            except ValueError as exc:
                typer.secho(str(exc), fg=RED)
            finally:
                db.close()

    if not_mached:
        csv_export(dbc.MAIN_DIR / dbc.DATA_DIR / "not_mached.csv", not_mached)
        typer.echo(
            f"Saved the list of {len(not_mached)} not matched institutions."
        )

    if fuzz:
        csv_export(dbc.MAIN_DIR / dbc.DATA_DIR / "fuzz.csv", fuzz)
        typer.echo(f"Saved the list of {len(fuzz)} fuzzy-matched institutions.")

    typer.secho("All done!", fg=GREEN)
