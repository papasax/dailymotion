"""
User Data Access Object (DAO).
Handles all raw SQL interactions with the PostgreSQL database for the users table.
"""

from typing import Optional, Any, Dict

from pydantic import EmailStr

from app.db import get_db_connection


class UserRepo:
    """
    Repository class for user-related database operations.
    Provides static methods to interact with the 'users' table using raw SQL.
    """

    @staticmethod
    async def create(
        email: str, password_hash: str, code: str, expires_at: float
    ) -> None:
        """Inserts a new user record asynchronously."""
        async for conn in get_db_connection():
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO users (email, password_hash, activation_code, code_expires_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (email, password_hash, code, expires_at),
                )

    @staticmethod
    async def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user record asynchronously by email."""
        async for conn in get_db_connection():
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                return await cur.fetchone()

    @staticmethod
    async def set_active(email: EmailStr) -> None:
        """
        Updates a user's status to active in the database.
        """
        async for conn in get_db_connection():
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE users SET is_active = TRUE WHERE email = %s", (email,)
                )
