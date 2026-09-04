from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

from src.schemas.errors import ErrorResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

async def sql_alchemy_error_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:

    logger.exception(
        'Database exception occured method=%s, path=%s, detail=%s',
        request.method,
        request.url.path,
        str(exc)
    )

    content = ErrorResponse(
        detail='Database Error.'
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content.model_dump()
    )