"""Route functions to process requests and return data to the client"""

from fastapi import APIRouter

from rankr.api.v1.routers.institution import router as institution_router
from rankr.api.v1.routers.ranking import router as ranking_router


router = APIRouter()

router.include_router(institution_router, prefix="/i", tags=["institution"])
router.include_router(ranking_router, prefix="/r", tags=["ranking"])
