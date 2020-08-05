from typing import List

from sqlalchemy.orm import Session
from tqdm import tqdm

from config import DBConfig
from rankr.db_models import (
    Acronym,
    Alias,
    Country,
    Institution,
    Link,
    Type,
    SessionLocal,
)
from utils import csv_size, get_csv, get_row, nullify

# processing countries
try:
    db: Session = SessionLocal()
    rows = get_row(DBConfig.MAIN_DIR / "countries.csv")
    countries_list: List[Country] = []
    for row in rows:
        nullify(row)
        countries_list.append(Country(**row))
    if countries_list:
        db.add_all(countries_list)
        db.commit()
finally:
    db.close()

# processing institutions
try:
    print("Processing institutions ...")
    db: Session = SessionLocal()

    institution_attrs = [
        get_csv(DBConfig.GRID_DATABASE_DIR / f"{attr}.csv", "grid_id")
        for attr in ["addresses", "acronyms", "aliases", "links", "types"]
    ]
    countries = {c.country: c for c in db.query(Country).all()}
    rows = get_row(DBConfig.GRID_DATABASE_DIR / "institutes.csv")
    row_count = csv_size(DBConfig.GRID_DATABASE_DIR / "institutes.csv")

    pbar = tqdm(total=row_count)
    for row in tqdm(rows):
        nullify(row)
        address, acronym, alias, link, type = [
            attr.get(row["grid_id"]) for attr in institution_attrs
        ]

        if address:
            country = DBConfig.country_name_mapper(address[0].pop("country"))
            institution = Institution(**{**row, **address[0]})
            institution.country = countries[country]
        else:
            institution = Institution(**row)

        if acronym:
            institution.acronyms = [Acronym(**i) for i in acronym]
        if alias:
            institution.aliases = [Alias(**i) for i in alias]
        if link:
            institution.links = [Link(**i) for i in link]
        if type:
            institution.types = [Type(**i) for i in type]

        db.add(institution)
        pbar.update(1)
    pbar.close()

    print("Committing results to the database...")
    db.commit()
finally:
    del institution_attrs
    db.close()
