"""
Database management module.
Handles connection pooling, retry logic for container startup, and table initialization.
"""

import logging
from typing import Optional, AsyncGenerator
import psycopg
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global async pool instance
DB_POOL: Optional[AsyncConnectionPool] = None


class DatabaseManager:
    """
    Manages the lifecycle of the asynchronous database connection pool.
    """

    pool: Optional[AsyncConnectionPool] = None

    @classmethod
    async def init_pool(cls) -> None:
        """Initializes the global async connection pool."""
        if cls.pool is None:
            cls.pool = AsyncConnectionPool(
                conninfo=settings.database_url,
                min_size=2,
                max_size=10,
                open=False,  # Don't open in constructor to avoid warning
                kwargs={"row_factory": dict_row, "autocommit": True},
            )
            await cls.pool.open()  # Explicitly open the pool
            await cls.pool.wait()
            logger.info("Async database connection pool initialized.")

    @classmethod
    async def close_pool(cls) -> None:
        """Closes the global async connection pool."""
        if cls.pool:
            await cls.pool.close()
            cls.pool = None
            logger.info("Async database connection pool closed.")


async def get_db_connection() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """Async context manager to get a connection from the pool."""
    if DatabaseManager.pool is None:
        raise RuntimeError("Database pool not initialized.")

    async with DatabaseManager.pool.connection() as conn:
        yield conn


# Exporting these for easier imports in main.py
init_pool = DatabaseManager.init_pool
close_pool = DatabaseManager.close_pool


async def init_db() -> None:
    """
    Initializes the database schema asynchronously.
    Creates the 'users' table if it does not already exist.
    """
    logger.info("Ensuring database schema is initialized...")
    async for conn in get_db_connection():
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    activation_code TEXT,
                    code_expires_at DOUBLE PRECISION,
                    is_active BOOLEAN DEFAULT FALSE
                );
            """
            )
            # autocommit is True in pool config, but explicit commit is safe
            await conn.commit()
    logger.info("Database initialization complete.")
