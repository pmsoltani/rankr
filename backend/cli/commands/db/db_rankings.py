from contextlib import closing
from pathlib import Path
from typing import List

import typer
from sqlalchemy.orm import Session
from typer.colors import CYAN, GREEN

from config import crwc, dbc
from rankr.crud import ranking_process
from rankr import db_models as d
from utils import csv_export


def db_rankings(
    commit: bool = typer.Option(True, help="Commit the results to the DB?")
):
    """Populates the database with ranking data."""
    db: Session
    with closing(d.SessionLocal()) as db:
        all_institutions: List[d.Institution] = db.query(d.Institution).all()
        soup = {}  # Group soup by country for better performance.
        for inst in all_institutions:
            try:
                soup[inst.country.country][inst.soup] = inst.grid_id
            except KeyError:
                soup[inst.country.country] = {inst.soup: inst.grid_id}

    not_mached = []
    fuzz = []
    for ranking_system in list(crwc.RANKINGS["metrics"]):
        # Get the ranking system directory.
        dir_path: Path = dbc.DATA_DIR / ranking_system
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
            with closing(d.SessionLocal()) as db:
                institutions_list, not_mached_list, fuzz_list = ranking_process(
                    db=db, file_path=file, soup=soup
                )
                not_mached.extend(not_mached_list)
                fuzz.extend(fuzz_list)
                if commit:
                    db.add_all(institutions_list)
                    db.commit()

    if not_mached:
        csv_export(dbc.DATA_DIR / "not_mached.csv", not_mached)
        typer.echo("Saved the list of not matched institutions.")
    if fuzz:
        csv_export(dbc.DATA_DIR / "fuzz.csv", fuzz)
        typer.echo("Saved the list of fuzzy-matched institutions.")

    typer.secho("All done!", fg=GREEN)
