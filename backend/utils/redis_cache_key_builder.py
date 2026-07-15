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

    # Build the key from the path + query params sorted by name, so that the
    # same logical request always maps to one key regardless of param order.
    # (Using the raw request.url meant "?a=1&b=2" and "?b=2&a=1" — or any bot
    # appending junk params — created separate, long-lived cache entries.)
    query = "&".join(f"{k}={v}" for k, v in sorted(request.query_params.multi_items()))
    path_with_query = f"{request.url.path}?{query}" if query else request.url.path
    return ":".join(
        map(
            str,
            [prefix, namespace, func.__module__, func.__name__, path_with_query],
        )
    )
