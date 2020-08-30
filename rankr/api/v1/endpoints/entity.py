from fastapi import APIRouter, Depends, HTTPException

from rankr.api import deps
from rankr.crud.entity import Entity
from rankr.enums import EntityTypeEnum
from rankr.schemas import EntitySchema


router = APIRouter()


@router.get("/i/{entity}", response_model=EntitySchema)
async def get_institution_entity(commons: dict = Depends(deps.resolve_entity)):
    try:
        if commons["entity_type"] != EntityTypeEnum.institution:
            raise HTTPException(status_code=404)
        institution_entity = Entity(**commons)
        return institution_entity.profile
    except Exception:
        raise


@router.get("/geo/{entity}", response_model=EntitySchema)
async def get_geo_entity(
    commons: dict = Depends(deps.resolve_entity), remove_nulls: bool = True
):
    try:
        if commons["entity_type"] == EntityTypeEnum.institution:
            raise HTTPException(status_code=404)
        geo_entity = Entity(**commons, remove_nulls=remove_nulls)
        return geo_entity.profile
    except Exception:
        raise
