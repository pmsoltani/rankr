from fastapi import APIRouter, Depends

from rankr import repos as r, schemas as s
from rankr.api.dependencies import get_repo


router = APIRouter()


@router.get(
    "/", name="search:site search", response_model=s.SearchResults,
)
def site_search(
    q: str = None,
    offset: int = 0,
    limit: int = 8,
    institution_repo: r.InstitutionRepo = Depends(get_repo(r.InstitutionRepo)),
):
    db_institutions = institution_repo.get_institutions(
        search_query=q, offset=offset, limit=limit
    )
    return s.SearchResults(institutions=db_institutions)
