"""MongoDB connection lifecycle managed via FastAPI lifespan."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

_client: AsyncMongoClient | None = None
_database: AsyncDatabase | None = None


def get_database() -> AsyncDatabase:
    """Return the active database instance. Raises if called before startup."""
    if _database is None:
        raise RuntimeError("Database not initialised — app lifespan not started.")
    return _database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Connect to MongoDB on startup, disconnect on shutdown."""
    global _client, _database

    _client = AsyncMongoClient(settings.DB_URL)
    _database = _client[settings.DB_NAME]

    # Verify connectivity
    await _client.admin.command("ping")
    logger.info("Connected to MongoDB: %s", settings.DB_NAME)

    yield

    await _client.close()
    logger.info("MongoDB connection closed.")
