from fastapi import APIRouter, Depends, HTTPException, status

from rankr import repos as r
from rankr.api.dependencies import get_repo


router = APIRouter()


@router.get("/healthcheck", name="healthcheck", status_code=status.HTTP_200_OK)
def perform_healthcheck(
    ranking_repo: r.RankingRepo = Depends(get_repo(r.RankingRepo)),
):
    try:
        systems = ranking_repo.get_ranking_systems()
        if systems:
            return {"healthcheck": "Everything OK!"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server problem!",
        )
