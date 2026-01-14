from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.endpoints import router
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform database initialization (ensure tables exist)
    init_db()
    yield

app = FastAPI(title="User Registration API", lifespan=lifespan)

app.include_router(router, prefix="/api/v1")
