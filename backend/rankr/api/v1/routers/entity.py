from typing import List
from fastapi import APIRouter, Depends, HTTPException

from config import appc, enums as e
from rankr import schemas as s
from rankr.api.dependencies import (
    check_entities,
    get_entity_type,
    resolve_entity,
)
from rankr.crud import Entity


router = APIRouter()


@router.get("/i/{entity}", response_model=s.EntitySchema)
async def get_institution_entity(commons: dict = Depends(resolve_entity)):
    """Returns the profile for an institution."""
    try:
        if commons["entity_type"] != e.EntityTypeEnum["institution"]:
            raise HTTPException(status_code=404)
        institution_entity = Entity(**commons)
        return institution_entity.profile
    except Exception:
        raise


@router.get("/geo/{entity}", response_model=s.EntitySchema)
async def get_geo_entity(
    commons: dict = Depends(resolve_entity),
    remove_nulls: bool = True,
    fresh: bool = False,
):
    """Returns the profile for a geo entity."""
    try:
        if commons["entity_type"] == e.EntityTypeEnum["institution"]:
            raise HTTPException(status_code=404)
        geo_entity = Entity(**commons, remove_nulls=remove_nulls, fresh=fresh)
        return geo_entity.profile
    except Exception:
        raise


@router.get(
    "/{entity_type_path}/{entity}/compare", response_model=List[s.EntitySchema]
)
async def entity_compare(
    entity_type_path: e.EntityTypePathEnum,
    commons: dict = Depends(resolve_entity),
    entities: List[str] = Depends(check_entities),
    remove_nulls: bool = True,
    fresh: bool = False,
):
    """Compares the profiles of the specified entities."""
    entity_type = commons["entity_type"].name
    if appc.ENTITIES["entity_types"][entity_type] != entity_type_path.name:
        raise HTTPException(status_code=404)

    entities_list: List[Entity] = [Entity(**commons).profile]
    for entity in entities:
        entity_type = get_entity_type(db=commons["db"], entity=entity)
        entities_list.append(
            Entity(
                db=commons["db"],
                entity=entity,
                entity_type=entity_type[0],
                name=entity_type[1],
                remove_nulls=remove_nulls,
                fresh=fresh,
            ).profile
        )

    return entities_list
