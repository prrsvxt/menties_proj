from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.schemas.errors import ErrorResponse
from src.exceptions.general_errors import ConflictError

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

async def conflict_error_handler(
        request: Request,
        exc: ConflictError
) -> JSONResponse:

    logger.exception(
        'Conflict creation methd=%s, path=%s, detail=%s',
        request.method,
        request.url.path,
        str(exc)
    )

    content = ErrorResponse(
        detail='Conflict Error.'
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=content.model_dump()
    )