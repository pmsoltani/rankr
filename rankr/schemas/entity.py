from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from rankr.enums import EntityTypeEnum
from rankr.schemas.ranking import RankingSchema


class EntitySchema(BaseModel):
    """For returning an institution/geo entity to the client."""

    entity: str
    entity_type: EntityTypeEnum
    url: HttpUrl
    name: str
    wikipedia_url: Optional[HttpUrl] = None
    established: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    ranks: List[RankingSchema]
    scores: List[RankingSchema]
    stats: List[RankingSchema]

    class Config:
        orm_mode = True
