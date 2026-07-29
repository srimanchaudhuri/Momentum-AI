"""Global exception handlers registered on the FastAPI app."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AppException
from app.logger import get_logger

logger = get_logger("exceptions")


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the app instance."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        """Handle all domain exceptions (NotFoundError, DuplicateError, etc.)."""
        logger.warning("%s [%d]: %s", exc.__class__.__name__, exc.status_code, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unexpected errors — log the traceback, return a clean 500."""
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )
