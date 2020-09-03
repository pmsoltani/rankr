from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from rankr.api import deps
from rankr.crud import get_ranking_systems, get_ranking_table
from rankr.enums import RankingSystemEnum
from rankr.schemas import RankingSchema


router = APIRouter()


@router.get(
    "/ranking_systems", response_model=Dict[RankingSystemEnum, List[int]]
)
async def ranking_systems(db: Session = Depends(deps.get_db)):
    return get_ranking_systems(db=db)


@router.get(
    "/{ranking_system}/{year}",
    response_model=Dict[RankingSystemEnum, List[RankingSchema]],
)
def ranking(
    *,
    db: Session = Depends(deps.get_db),
    year: int,
    ranking_system: RankingSystemEnum,
):
    return get_ranking_table(db=db, year=year, ranking_system=ranking_system)
