from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, Field

from config import enums as e
from rankr.schemas.core import OrmBase


class RankingBase(BaseModel):
    id: Optional[int]
    institution_id: Optional[int]

    ranking_system: e.RankingSystemEnum
    ranking_type: e.RankingTypeEnum
    year: int = Field(..., ge=2004)
    field: str
    subject: str

    metric: e.MetricEnum
    value: Union[Decimal, int, None]
    value_type: e.ValueTypeEnum


class RankingCreate(RankingBase):
    pass


class RankingOut(RankingBase):
    pass


class RankingDB(RankingOut, OrmBase):
    pass
