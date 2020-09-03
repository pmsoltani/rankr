import re
from typing import Any, Dict, Generator, List, Tuple

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from config import appc
from rankr.db_models import Country, Institution, SessionLocal
from rankr.enums import EntityTypeEnum
from utils import get_csv


country_code_mapper = get_csv(appc.COUNTRIES_FILE, "country_code")


def get_db() -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for the CRUD operations."""
    try:
        db: Session = SessionLocal()
        yield db
    finally:
        db.close()


def get_geo_data(db: Session) -> Dict[str, List[str]]:
    """Retrieves all countries with ranked institutions."""
    countries_list: List[Country] = (
        db.query(Country)
        .join(Country.institutions)
        .join(Institution.rankings)
        .group_by(Country)
        .all()
    )
    geo_data = {
        "regions": set(),
        "sub_regions": set(),
        "countries": set(),
        "country_codes": set(),
    }
    for country in countries_list:
        geo_data["regions"].add(country.region)
        geo_data["sub_regions"].add(country.sub_region)
        geo_data["countries"].add(country.country)
        geo_data["country_codes"].add(country.country_code)

    return {geo: sorted(data) for geo, data in geo_data.items()}


geo_data: Dict[str, List[str]] = {}


def get_entity_type(db: Session, entity: str) -> Tuple[EntityTypeEnum, str]:
    """Decides the type of the entity

    Args:
        db (Session): SQLAlchemy session instant to connect to the DB
        entity (str): The input entity from the client

    Raises:
        HTTPException: If the type of the entity cannot be decided

    Returns:
        Tuple[EntityTypeEnum, str]: Type of the entity and its name (if
        entity type is "country_code" or "world")
    """
    global geo_data
    geo_data = geo_data or get_geo_data(db=db)

    entity_type = None
    name = None
    if re.match(appc.GRID_ID_PATTERN, entity):
        entity_type = EntityTypeEnum["institution"]
    if entity.lower() == "world":
        entity_type = EntityTypeEnum["world"]
        name = entity.title()
    if entity in geo_data["regions"]:
        entity_type = EntityTypeEnum["region"]
    if entity in geo_data["sub_regions"]:
        entity_type = EntityTypeEnum["sub_region"]
    if entity in geo_data["countries"]:
        entity_type = EntityTypeEnum["country"]
    if entity in geo_data["country_codes"]:
        entity_type = EntityTypeEnum["country_code"]
        name = country_code_mapper[entity][0]["country"]

    if not entity_type:
        raise HTTPException(
            status_code=404, detail=f"Invalid 'entity' value: '{entity}'"
        )

    return (entity_type, name if name else entity)


async def resolve_entity(
    *, db: Session = Depends(get_db), entity: str
) -> Dict[str, Any]:
    """Dependency for some of the routes"""
    entity_type = get_entity_type(db=db, entity=entity)
    return {
        "db": db,
        "entity": entity,
        "entity_type": entity_type[0],
        "name": entity_type[1],
    }
