from typing import List

from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from config import DBConfig
from rankr.db_models import (
    Acronym,
    Alias,
    Base,
    engine,
    SessionLocal,
    Institution,
    Link,
    # Ranking,
    Type,
)
from utils import get_row, nullify, whole_csv


if not database_exists(engine.url):
    encoding = "utf8mb4" if DBConfig.DIALECT == "mysql" else "utf8"
    create_database(engine.url, encoding=encoding)

Base.metadata.create_all(engine)
db: Session


# institutions
try:
    institution_attrs = [
        whole_csv(DBConfig.GRID_DATABASE_DIR / f"{attr}.csv", "grid_id")
        for attr in ["addresses", "acronyms", "aliases", "links", "types"]
    ]
    db = SessionLocal()
    rows = get_row(DBConfig.GRID_DATABASE_DIR / "institutes.csv")
    institutions_list: List[Institution] = []
    for row in rows:
        nullify(row)
        grid_id = row["grid_id"]
        address, acronym, alias, link, type = [
            attr.get(grid_id) for attr in institution_attrs
        ]
        if address:
            institution = Institution(**{**row, **address[0]})
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

        institutions_list.append(institution)

    if institutions_list:
        db.add_all(institutions_list)
        db.commit()
finally:
    del institution_attrs
    db.close()
