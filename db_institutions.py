from typing import List

from sqlalchemy.orm import Session

from config import DBConfig
from rankr.db_models import (
    Acronym,
    Alias,
    SessionLocal,
    Institution,
    Link,
    Type,
)
from utils import get_row, nullify, whole_csv

try:
    institution_attrs = [
        whole_csv(DBConfig.GRID_DATABASE_DIR / f"{attr}.csv", "grid_id")
        for attr in ["addresses", "acronyms", "aliases", "links", "types"]
    ]
    db: Session = SessionLocal()
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
