"""
Main entry point for the User Registration API.
Handles application initialization, lifespan events, and router inclusion.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router
from app.db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    """
    Handles application startup and shutdown events.
    Ensures the database is initialized before the app starts.
    """
    # Perform database initialization (ensure tables exist)
    init_db()
    logger.info("Application startup: Database tables ensured.")
    yield
    logger.info("Application shutdown: Cleaning up resources.")


app = FastAPI(title="User Registration API", lifespan=lifespan)

app.include_router(router, prefix="/api/v1")
