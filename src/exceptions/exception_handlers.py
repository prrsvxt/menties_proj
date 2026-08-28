from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from .general_errors import NotFoundError

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
    
    return JSONResponse(
        status_code=404,
        content={'detail': str(exc)}
    )