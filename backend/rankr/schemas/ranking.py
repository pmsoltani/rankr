from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, Field, validator

from config import enums as e
from rankr.schemas.core import OrmBase
from rankr.schemas.validators import basic_process, value_process


class RankingBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]

    ranking_system: e.RankingSystemEnum
    ranking_type: e.RankingTypeEnum
    year: int = Field(..., ge=2004)
    field: str
    subject: str

    metric: e.MetricEnum
    raw_value: Optional[str]
    value_type: e.ValueTypeEnum
    value: Union[Decimal, int, str, None]

    # validators
    _clean_raw_value = validator("raw_value", allow_reuse=True, pre=True)(
        basic_process
    )

    @validator("value", always=True)
    def _coerce_value(cls, value, values):
        return value_process(
            value=values["raw_value"], value_type=values["value_type"].name
        )


class RankingCreate(RankingBase):
    institution_id: int


class RankingOut(RankingBase):
    pass


class RankingDB(OrmBase, RankingBase):
    pass
