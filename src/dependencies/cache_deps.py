from fastapi import Request

from src.cache.redis_cache import RedisCache


def get_redis(request: Request) -> RedisCache:
    return request.app.state.redis