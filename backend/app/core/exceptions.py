from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger("app.exceptions")

class PitchAnalyserException(Exception):
    """Base exception for Pitch Analyser application."""
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(self.detail)

class NotFoundException(PitchAnalyserException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND"
        )

class AuthenticationException(PitchAnalyserException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED"
        )

class ForbiddenException(PitchAnalyserException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN"
        )

class BadRequestException(PitchAnalyserException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST"
        )

class FileTooLargeException(PitchAnalyserException):
    def __init__(self, detail: str = "File size exceeds the 100MB limit"):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=detail,
            error_code="FILE_TOO_LARGE"
        )

class InvalidFileFormatException(PitchAnalyserException):
    def __init__(self, detail: str = "Unsupported file format"):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=detail,
            error_code="UNSUPPORTED_MEDIA_TYPE"
        )

class ProcessingException(PitchAnalyserException):
    def __init__(self, detail: str = "AI processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="PROCESSING_ERROR"
        )

def register_exception_handlers(app: FastAPI):
    """Registers global exception handlers for mapping uniform JSON responses."""
    
    @app.exception_handler(PitchAnalyserException)
    async def custom_exception_handler(request: Request, exc: PitchAnalyserException):
        logger.warning(f"Application error code {exc.error_code} raised on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_code": exc.error_code}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Request validation failure on {request.url.path}: {exc.errors()}")
        # Parse Pydantic validation errors into readable strings
        errors = exc.errors()
        error_details = []
        for err in errors:
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            msg = err.get("msg", "invalid field value")
            error_details.append(f"{loc}: {msg}")
            
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "; ".join(error_details),
                "error_code": "VALIDATION_ERROR"
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database SQLAlchemy error raised on {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database error occurred. Please contact the administrator.",
                "error_code": "DATABASE_ERROR"
            }
        )

    @app.exception_handler(Exception)
    async def fallback_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server exception on {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred.",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )
