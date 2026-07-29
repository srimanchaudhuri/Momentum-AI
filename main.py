"""Momentum AI — FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings
from app.database import lifespan
from app.exception_handlers import register_exception_handlers
from routers import users

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# ── Exception handlers ────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ────────────────────────────────────────────────────────────────
app.include_router(users.router, prefix="/api/users", tags=["Users"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}