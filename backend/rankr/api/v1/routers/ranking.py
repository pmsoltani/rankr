from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from config import enums as e
from rankr import repos as r, schemas as s
from rankr.api.dependencies import get_repo


router = APIRouter()


@router.get(
    "/i/metric",
    name="ranking:get rankings by institution ids",
    response_model=List[s.RankingOut],
)
def get_rankings_by_institution_ids(
    *,
    institution_ids: List[int] = Query([]),
    ranking_system: e.RankingSystemEnum,
    ranking_type: e.RankingTypeEnum = e.RankingTypeEnum["university ranking"],
    metric: e.MetricEnum,
    field: str = "All",
    subject: str = "All",
    offset: int = 0,
    limit: Optional[int] = 25,
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    return ranking_repo.get_rankings_by_institution_ids(
        institution_ids=institution_ids,
        ranking_system=ranking_system,
        ranking_type=ranking_type,
        metric=metric,
        field=field,
        subject=subject,
        offset=offset,
        limit=limit,
    )
