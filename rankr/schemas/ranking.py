from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, root_validator

from rankr.db_models import Institution
from rankr.enums import (
    EntityTypeEnum,
    MetricEnum,
    RankingSystemEnum,
    RankingTypeEnum,
    ValueTypeEnum,
)


class RankingSchema(BaseModel):
    ranking_system: RankingSystemEnum
    ranking_type: RankingTypeEnum
    year: int
    field: str
    subject: str
    metric: MetricEnum
    value_type: ValueTypeEnum
    value: Union[Decimal, int, None]
    entity: Union[str, List[str]]
    entity_type: EntityTypeEnum
    name: Optional[str] = None
    country: Optional[str] = None

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def _get_ranking_row_data(cls, input_values: dict) -> dict:
        result = {**input_values}
        institution: Optional[Institution] = result.get("institution")
        if institution:
            result["entity"] = result.get("entity") or institution.grid_id
            result["entity_type"] = (
                result.get("entity_type") or EntityTypeEnum["institution"]
            )
            result["name"] = institution.name
            result["country"] = institution.country.country
            result["country_code"] = institution.country.country_code
        return result
