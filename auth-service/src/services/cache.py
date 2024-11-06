from functools import lru_cache
from fastapi import Depends
from redis.asyncio import Redis

from db.redis import get_redis
from services.base import BaseSetKey, BaseGetByKey


class CacheServise(BaseSetKey, BaseGetByKey):
    def __init__(self, redis: Redis):
        self.redis = redis


@lru_cache()
def get_cache_service(
    redis: Redis = Depends(get_redis),
) -> CacheServise:
    return CacheServise(redis)
