from typing import Dict, List, Optional

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
    metrics: List[e.MetricEnum] = Query([]),
    year: Optional[int] = None,
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
        metrics=metrics,
        year=year,
        field=field,
        subject=subject,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/ranks",
    name="ranking:get ranks by institution id",
    response_model=List[s.RankingOut],
)
def get_ranks_by_institution_id(
    institution_id: int,
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    return ranking_repo.get_ranks_by_institution_id(
        institution_id=institution_id,
    )


@router.get(
    "/scores",
    name="ranking:get scores by institution id",
    response_model=List[s.RankingOut],
)
def get_scores_by_institution_id(
    institution_id: int,
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    return ranking_repo.get_scores_by_institution_id(
        institution_id=institution_id,
    )


@router.get(
    "/systems",
    name="ranking:get ranking systems",
    response_model=Dict[e.RankingSystemEnum, List[int]],
)
def get_ranking_systems(
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    return ranking_repo.get_ranking_systems()


@router.get(
    "/table/{ranking_system}/{year}",
    name="ranking:get ranking table",
    response_model=List[s.RankingTableRow],
)
def get_ranking_table(
    ranking_system: e.RankingSystemEnum,
    year: int,
    ranking_type: e.RankingTypeEnum = e.RankingTypeEnum["university ranking"],
    field: str = "All",
    subject: str = "All",
    offset: int = 0,
    limit: Optional[int] = 25,
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    return ranking_repo.get_ranking_table(
        ranking_system=ranking_system,
        ranking_type=ranking_type,
        year=year,
        field=field,
        subject=subject,
        offset=offset,
        limit=limit,
    )
