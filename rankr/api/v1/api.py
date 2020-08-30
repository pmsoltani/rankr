from fastapi import APIRouter

from rankr.api.v1.endpoints import ranking

api_router = APIRouter()
api_router.include_router(ranking.router, prefix="/ranking")
