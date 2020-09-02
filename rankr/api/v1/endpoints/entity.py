from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query

from config import APPConfig
from rankr.api import deps
from rankr.crud.entity import Entity
from rankr.enums import EntityTypeEnum, EntityTypePathEnum
from rankr.schemas import EntitySchema


router = APIRouter()


@router.get("/i/{entity}", response_model=EntitySchema)
async def get_institution_entity(commons: dict = Depends(deps.resolve_entity)):
    """Returns the profile for an institution."""
    try:
        if commons["entity_type"] != EntityTypeEnum["institution"]:
            raise HTTPException(status_code=404)
        institution_entity = Entity(**commons)
        return institution_entity.profile
    except Exception:
        raise


@router.get("/geo/{entity}", response_model=EntitySchema)
async def get_geo_entity(
    commons: dict = Depends(deps.resolve_entity), remove_nulls: bool = True
):
    """Returns the profile for a geo entity."""
    try:
        if commons["entity_type"] == EntityTypeEnum["institution"]:
            raise HTTPException(status_code=404)
        geo_entity = Entity(**commons, remove_nulls=remove_nulls)
        return geo_entity.profile
    except Exception:
        raise


@router.get(
    "/{entity_type_path}/{entity}/compare",
    response_model=Tuple[EntitySchema, List[EntitySchema]],
)
async def entity_compare(
    entity_type_path: EntityTypePathEnum,
    commons: dict = Depends(deps.resolve_entity),
    entities: List[str] = Query(str),
    remove_nulls: bool = True,
):
    """Compares the profiles of the specified entities."""
    entity_type = commons["entity_type"].name
    if APPConfig.ENTITIES["entity_types"][entity_type] != entity_type_path.name:
        raise HTTPException(status_code=404)

    institution = Entity(**commons).profile
    entities_list: List[Entity] = []
    for entity in entities:
        entity_type = deps.get_entity_type(db=commons["db"], entity=entity)
        entities_list.append(
            Entity(
                db=commons["db"],
                entity=entity,
                entity_type=entity_type[0],
                name=entity_type[1],
                remove_nulls=remove_nulls,
            ).profile
        )

    return (institution, entities_list)
