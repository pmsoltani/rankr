"""Route functions to process requests and return data to the client"""

from fastapi import APIRouter

from rankr.api.v1.routers.healthcheck import router as healthcheck_router
from rankr.api.v1.routers.institution import router as institution_router
from rankr.api.v1.routers.ranking import router as ranking_router
from rankr.api.v1.routers.search import router as search_router


router = APIRouter()

router.include_router(healthcheck_router, tags=["healthcheck"])
router.include_router(institution_router, prefix="/i", tags=["institution"])
router.include_router(ranking_router, prefix="/r", tags=["ranking"])
router.include_router(search_router, prefix="/s", tags=["search"])
