from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from config import enums as e
from rankr.schemas.ranking import RankingBase


class EntityBase(BaseModel):
    """For returning an institution/geo entity to the client."""

    entity: str
    entity_type: e.EntityTypeEnum
    url: HttpUrl
    name: str
    wikipedia_url: Optional[HttpUrl] = None
    established: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    ranks: List[RankingBase]
    scores: List[RankingBase]
    stats: List[RankingBase]

    @validator("country", always=True)
    def _validate_country(cls, country, values: dict) -> Optional[str]:
        pass
