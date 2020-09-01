from typing import List

import typer
from sqlalchemy.orm import Session
from tqdm import tqdm
from typer.colors import CYAN

from config import DBConfig
from rankr.db_models import (
    Acronym,
    Alias,
    Country,
    Institution,
    Label,
    Link,
    Type,
    SessionLocal,
)
from utils import csv_size, get_csv, get_row, nullify


def db_grid():
    try:
        typer.secho("Processing countries...", fg=CYAN)
        db: Session = SessionLocal()
        rows = get_row(DBConfig.MAIN_DIR / "countries.csv")
        countries_list: List[Country] = []
        for row in rows:
            nullify(row)
            countries_list.append(Country(**row))

        db.add_all(countries_list)
        db.commit()
    finally:
        db.close()

    attrs = ["addresses", "acronyms", "aliases", "labels", "links", "types"]

    try:
        typer.secho("Processing institutions...", fg=CYAN)
        db: Session = SessionLocal()

        institution_attrs = [
            get_csv(DBConfig.GRID_DATABASE_DIR / f"{attr}.csv", "grid_id")
            for attr in attrs
        ]
        countries = {c.country: c for c in db.query(Country).all()}
        rows = get_row(DBConfig.GRID_DATABASE_DIR / "institutes.csv")
        row_count = csv_size(DBConfig.GRID_DATABASE_DIR / "institutes.csv")

        pbar = tqdm(total=row_count)
        for row in rows:
            nullify(row)
            address, acronym, alias, label, link, type = [
                attr.get(row["grid_id"]) for attr in institution_attrs
            ]

            soup = [row["name"]]

            if address:
                country = DBConfig.country_name_mapper(
                    address[0].pop("country")
                )
                institution = Institution(**{**row, **address[0]})
                institution.country = countries[country]
                soup.append(country)
            else:
                institution = Institution(**row)

            if acronym:
                institution.acronyms = [Acronym(**i) for i in acronym]
                soup.extend(i["acronym"] for i in acronym)
            if alias:
                institution.aliases = [Alias(**i) for i in alias]
                soup.extend(i["alias"] for i in alias)
            if label:
                institution.labels = [Label(**i) for i in label]
                soup.extend(i["label"] for i in label)
            if link:
                institution.links = [Link(**i) for i in link]
            if type:
                institution.types = [Type(**i) for i in type]

            institution.soup = " | ".join(i for i in soup)

            db.add(institution)
            pbar.update()
        pbar.close()

        typer.secho(
            "Committing results to the DB. This can take several minutes.",
            fg=CYAN,
        )
        db.commit()
    finally:
        del institution_attrs
        db.close()
