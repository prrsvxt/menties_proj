import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.router.v1.router import router_v1
from src.exceptions.exception_handlers import not_found_error_handler
from src.exceptions.general_errors import NotFoundError
from src.logging_config import setup_logging

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    try:
        setup_logging()
        logger.info('Starting application initialization')

        app = FastAPI(
            docs_url='/docs',
            openapi_url='/openapi.json',
            default_response_class=JSONResponse,
        )

        logger.info('FastAPI app instance created')

        logger.info('Configuring middleware')
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        logger.info('Registering exception handlers')
        app.add_exception_handler(
            NotFoundError,
            not_found_error_handler
        )

        logger.info('Including application routers')
        app.include_router(router_v1)

        logger.info('Application initialized successfully')
        return app
    except Exception:
        logger.exception('Application startup failed')
        raise
