from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.router.v1.router import router_v1
from src.exceptions.exception_handlers import not_found_error_handler
from src.exceptions.general_errors import NotFoundError
from src.logging_config import setup_logging


def get_app() -> FastAPI:
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=JSONResponse,
    )

    setup_logging()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_exception_handler(
        NotFoundError,
        not_found_error_handler
    )
    
    app.include_router(router_v1)

    return app
