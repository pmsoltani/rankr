from fastapi import APIRouter, Depends, HTTPException, Path

from config import appc
from rankr import repos as r, schemas as s
from rankr.api.dependencies import get_repo


router = APIRouter()


@router.get(
    "/{institution_id}",
    name="institution:get institution by grid id",
    response_model=s.InstitutionOut,
)
def get_institution_by_grid_id(
    institution_id: str = Path(..., regex=appc.GRID_ID_PATTERN),
    institution_repo: r.InstitutionRepo = Depends(get_repo(r.InstitutionRepo)),
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    db_institution = institution_repo.get_institution_by_grid_id(
        grid_id=institution_id
    )
    if not db_institution:
        raise HTTPException(status_code=404, detail="Institution not found!")

    db_ranks = ranking_repo.get_ranks_by_institution_id(db_institution.id)
    db_stats = ranking_repo.get_stats_by_institution_id(db_institution.id)
    db_institution.ranks = db_ranks
    db_institution.stats = db_stats

    return db_institution
