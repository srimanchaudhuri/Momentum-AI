"""Momentum AI — FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings
from app.database import lifespan
from app.exception_handlers import register_exception_handlers
from routers import (
    auth,
    dashboard,
    goals,
    notifications,
    onboarding,
    plans,
    progress,
    users,
)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# ── Exception handlers ────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(plans.router, prefix="/api/goals", tags=["Plans & Resources"])
app.include_router(progress.router, prefix="/api/goals", tags=["Progress"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}