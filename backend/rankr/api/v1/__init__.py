"""Routes, dependencies, and other essentials for a functioning API"""

from fastapi import APIRouter

from rankr.api.v1.routers.entity import router as entity_router
from rankr.api.v1.routers.ranking import router as ranking_router


router = APIRouter()

router.include_router(entity_router, prefix="/entities", tags=["entities"])
router.include_router(ranking_router, prefix="/rankings", tags=["rankings"])
