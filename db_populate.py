from typing import List

from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from config import BaseConfig, DBConfig
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


def fill_attribute(attr: str, path: str, cls, db: Session):
    obj_list: List[cls] = []
    rows = get_row(path)
    for row in rows:
        nullify(row)
        institution: Institution = db.query(Institution).filter(
            Institution.grid_id == row["grid_id"]
        ).first()
        if not institution:
            continue
        row.pop("grid_id", None)
        obj = cls(**row)
        if attr == "links":
            obj.type = "homepage"
        if obj not in getattr(institution, attr):
            setattr(obj, "institution", institution)
        obj_list.append(obj)
    return obj_list


if not database_exists(engine.url):
    encoding = "utf8mb4" if DBConfig.DIALECT == "mysql" else "utf8"
    create_database(engine.url, encoding=encoding)

Base.metadata.create_all(engine)
db: Session

data_dir = BaseConfig.MAIN_DIR / "grid" / "full_tables"

# institutions
try:
    institution_attrs = [
        whole_csv(data_dir / f"{attr}.csv", "grid_id")
        for attr in ["addresses", "acronyms", "aliases", "links", "types"]
    ]
    db = SessionLocal()
    rows = get_row(data_dir / "institutes.csv")
    institutions_list: List[Institution] = []
    for row in rows:
        nullify(row)
        grid_id = row["grid_id"]
        address, acronym, alias, link, type = [
            attr.get(grid_id) for attr in institution_attrs
        ]
        if address:
            address = {
                k: v
                for k, v in address[0].items()
                if k
                in ["lat", "lng", "city", "state", "country", "country_code"]
            }
            institution = Institution(**{**row, **address})
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
