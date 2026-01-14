"""
Main entry point for the User Registration API.
Handles application initialization, lifespan events, and router inclusion.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router
from app.db import init_db


@asynccontextmanager
async def lifespan():
    """
    Handles application startup and shutdown events.
    Ensures the database is initialized before the app starts.
    """
    # Perform database initialization (ensure tables exist)
    init_db()
    yield


app = FastAPI(title="User Registration API", lifespan=lifespan)

app.include_router(router, prefix="/api/v1")
