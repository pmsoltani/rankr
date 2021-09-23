from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import FileResponse

from config import backc, wikic
from rankr import repos as r, schemas as s
from rankr.api.dependencies import get_repo


router = APIRouter()


@router.get(
    "/logo/{institution_id}",
    name="institution:get institution logo by grid id",
    response_class=FileResponse,
)
def get_institution_logo_by_grid_id(
    institution_id: str = Path(..., regex=backc.GRID_ID_PATTERN),
):
    for logoFormat in wikic.ALLOWED_LOGO_FORMATS:
        file_path = wikic.DOWNLOAD_DIR / f"{institution_id}{logoFormat}"
        if file_path.exists():
            return file_path

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Institution logo not found!",
    )


@router.get(
    "/{institution_id}",
    name="institution:get institution by grid id",
    response_model=s.InstitutionOut,
)
def get_institution_by_grid_id(
    institution_id: str = Path(..., regex=backc.GRID_ID_PATTERN),
    institution_repo: r.InstitutionRepo = Depends(get_repo(r.InstitutionRepo)),
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    db_institution = institution_repo.get_institution_by_grid_id(
        grid_id=institution_id
    )
    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found!",
        )

    db_ranks = ranking_repo.get_ranks_by_institution_id(db_institution.id)
    db_stats = ranking_repo.get_stats_by_institution_id(db_institution.id)
    db_institution.ranks = db_ranks
    db_institution.stats = db_stats

    return db_institution
