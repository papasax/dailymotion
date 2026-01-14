"""
Database management module.
Handles connection pooling, retry logic for container startup, and table initialization.
"""

import logging
import time
from typing import Optional

import psycopg
from psycopg.rows import dict_row
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_db_connection() -> psycopg.Connection:
    """
    Establishes a connection to the PostgreSQL database.
    Includes retry logic to wait for the database service to be ready.
    """
    # Database connection attempt with retry logic to wait for DNS/DB readiness
    retries: int = 5
    last_exception: Optional[Exception] = None

    while retries > 0:
        try:
            conn = psycopg.connect(settings.database_url, row_factory=dict_row)
            logger.info("Successfully connected to the database.")
            return conn
        except psycopg.OperationalError as e:
            last_exception = e
            retries -= 1
            if retries > 0:
                logger.warning(
                    "Database connection failed. Retrying in 2s... (%d retries left)",
                    retries,
                )
                time.sleep(2)

    if last_exception:
        logger.error("Failed to connect to the database after several retries.")
        raise last_exception
    raise psycopg.OperationalError(
        "Failed to connect to the database after several retries."
    )


def init_db() -> None:
    """
    Initializes the database schema.
    Creates the 'users' table if it does not already exist.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
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
            conn.commit()
