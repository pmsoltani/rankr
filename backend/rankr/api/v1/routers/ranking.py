from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import enums as e
from rankr import schemas as s
from rankr.api.dependencies import get_db
from rankr.crud import get_ranking_systems, get_ranking_table


router = APIRouter()


@router.get(
    "/ranking_systems", response_model=Dict[e.RankingSystemEnum, List[int]]
)
async def ranking_systems(db: Session = Depends(get_db)):
    return get_ranking_systems(db=db)


@router.get(
    "/{ranking_system}/{year}",
    response_model=Dict[e.RankingSystemEnum, List[s.RankingSchema]],
)
def ranking(
    *,
    db: Session = Depends(get_db),
    year: int,
    ranking_system: e.RankingSystemEnum,
):
    return get_ranking_table(db=db, year=year, ranking_system=ranking_system)
