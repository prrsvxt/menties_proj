from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
import logging

from src.schemas.errors import ErrorResponse


logger = logging.getLogger(__name__)

async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
):

    for error in exc.errors():
        location = error.get('loc', ())

        if location and location[-1] == 'timezone':
            logger.warning(
                'Invalid timezone method=%s path=%s detail=%s',
                request.method,
                request.url.path,
                str(exc)
            )

            context = error.get('ctx', {})
            original_error = context.get('error')
            detail = str(original_error or error.get('msg'))

            content = ErrorResponse(
                detail=detail
            )

            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content=content.model_dump()
            )

    return await request_validation_exception_handler(request, exc)
