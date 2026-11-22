from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import FastAPI
import logging
from redis import asyncio as redis_async

from src.config import Settings
from src.cache.redis_cache import RedisCache
from src.db import create_session_factory, create_engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine: AsyncEngine | None = None
    redis_cache: RedisCache | None = None

    try:
        settings = Settings()
        engine = create_engine(settings.postgres_url)
        session_factory = create_session_factory(engine)

        async with engine.connect() as connection:
            await connection.execute(text('SELECT 1'))

        redis_cache = RedisCache(
            redis_async.from_url(settings.redis_url),
            settings.cache_ttl,
        )
        
        ping = await redis_cache.ping()

        if not ping:
            raise Exception

        app.state.redis = redis_cache
        app.state.settings = settings
        app.state.engine = engine
        app.state.session_factory = session_factory
        logger.info('Application startup completed; database connection established')
    except Exception:
        logger.exception('Application startup failed')
        if redis_cache is not None:
            await redis_cache.close()
        if engine is not None:
            await engine.dispose()
        raise

    try:
        yield
    finally:
        await engine.dispose()
        await redis_cache.close()
        logger.info('Database engine disposed')
