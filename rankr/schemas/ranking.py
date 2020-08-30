from typing import Optional

from pydantic import BaseModel, root_validator

from rankr.db_models import Institution
from rankr.enums import RankingSystemEnum, RankingTypeEnum


class RankingRowSchema(BaseModel):
    rank: Optional[int]
    institution: str
    grid_id: str
    country: str
    ranking_system: RankingSystemEnum
    ranking_type: RankingTypeEnum
    year: int
    field: str
    subject: str

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def _get_ranking_row_data(cls, input_values: dict) -> dict:
        institution: Institution = input_values["institution"]
        return {
            **input_values,
            "rank": input_values["value"],
            "institution": institution.name,
            "grid_id": institution.grid_id,
            "country": institution.country.country,
        }
