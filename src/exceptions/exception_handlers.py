from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

from .general_errors import NotFoundError
from src.schemas.errors import ErrorResponse

logger = logging.getLogger(__name__)

async def not_found_error_handler(
    request: Request,
    exc: NotFoundError
) -> JSONResponse:

    logger.warning(
        'Resource not found method=%s path=%s detail=%s',
        request.method,
        request.url.path,
        str(exc)
    )

    content = ErrorResponse(
        detail=str(exc)
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=content.model_dump()
    )