from typing import Callable

import aioredis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from config import backc


def create_app_startup_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        redis = aioredis.from_url(
            backc.REDIS_URL,
            encoding=backc.REDIS_ENCODING,
            decode_responses=True,
        )
        FastAPICache.init(RedisBackend(redis), prefix="rankr-cache")

    return start_app


def create_app_shutdown_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await FastAPICache.clear(namespace="ranking-table")

    return stop_app
