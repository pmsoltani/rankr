from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from config import enums as e
from rankr.schemas.validators import basic_process, value_process


class RankingBase(BaseModel):
    id: int | None = None
    institution_id: int | None = None

    ranking_system: e.RankingSystemEnum
    ranking_type: e.RankingTypeEnum
    year: int = Field(..., ge=2004)
    field: str
    subject: str

    metric: e.MetricEnum
    raw_value: str | None = None
    value_type: e.ValueTypeEnum
    value: Decimal | int | str | None = None

    @field_validator("raw_value", mode="before")
    @classmethod
    def _clean_raw_value(cls, value):
        return basic_process(value)

    @model_validator(mode="after")
    def _coerce_value(self) -> "RankingBase":
        # Always derive `value` from the cleaned raw_value + its type, ignoring
        # any value passed in.
        self.value = value_process(
            value=self.raw_value, value_type=self.value_type.name
        )
        return self


class RankingCreate(RankingBase):
    institution_id: int
