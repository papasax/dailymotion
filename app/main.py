"""
Main entry point for the User Registration API.
Handles application initialization, lifespan events, and router inclusion.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router
from app.db import init_db, init_pool, close_pool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Handles application startup and shutdown events.
    Ensures the database is initialized before the app starts.
    """
    # Perform database initialization (ensure tables exist)
    # 1. Initialize the Async Connection Pool
    await init_pool()

    # 2. Perform database initialization (ensure tables exist)
    await init_db()
    logger.info("Application startup: Database tables ensured.")

    yield

    # 3. Clean up the pool on shutdown
    await close_pool()

    logger.info("Application shutdown: Cleaning up resources.")


app = FastAPI(title="User Registration API", lifespan=lifespan)

app.include_router(router, prefix="/api/v1")
