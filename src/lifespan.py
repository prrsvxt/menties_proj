from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import FastAPI
import logging

from src.config import Settings
from src.db import create_session_factory, create_engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine: AsyncEngine | None = None

    try:
        settings = Settings()
        engine = create_engine(settings.postgres_url)
        session_factory = create_session_factory(engine)

        async with engine.connect() as connection:
            await connection.execute(text('SELECT 1'))

        app.state.settings = settings
        app.state.engine = engine
        app.state.session_factory = session_factory
        logger.info('Application startup completed; database connection established')
    except Exception:
        logger.exception('Application startup failed')
        if engine is not None:
            await engine.dispose()
        raise

    try:
        yield
    finally:
        await engine.dispose()
        logger.info('Database engine disposed')
