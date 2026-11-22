from redis import asyncio as redis

class RedisCache:

    def __init__(self, redis_client: redis.Redis, ttl: int):
        self.redis_client = redis_client
        self.ttl = ttl

    async def get(self, key: str) -> str | None:
        response = await self.redis_client.get(key)
        if response is not None: 
            response = response.decode()
        return response

    async def set(
            self,
            key: str,
            value: str,
            nx: bool = False,
            use_ttl: bool = True,
    ) -> bool:
        ttl = self.ttl if use_ttl else None
        return await self.redis_client.set(key, value, ex=ttl, nx=nx)

    async def incr(self, key: str) -> int:
        return await self.redis_client.incr(key)

    async def delete(self, keys: list[str]) -> None:
        await self.redis_client.delete(*keys)

    async def ping(self) -> bool:
        return await self.redis_client.ping()

    async def close(self) -> None:
        await self.redis_client.aclose()

    
