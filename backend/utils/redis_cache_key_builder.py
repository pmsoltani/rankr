from typing import Callable, Optional

from fastapi import Request, Response
from fastapi_cache import FastAPICache


def redis_cache_key_builder(
    func: Callable,
    namespace: Optional[str],
    request: Request,
    response: Response,
    *args,
    **kwargs,
):
    if not namespace:
        namespace = ""
    prefix = FastAPICache.get_prefix() or ""
    return ":".join(
        map(
            str,
            [prefix, namespace, func.__module__, func.__name__, request.url],
        )
    )
