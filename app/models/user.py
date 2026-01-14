"""
User Data Access Object (DAO).
Handles all raw SQL interactions with the PostgreSQL database for the users table.
"""

from typing import Optional, Any, Dict
from app.db import get_db_connection


class UserRepo:
    """
    Repository class for user-related database operations.
    Provides static methods to interact with the 'users' table using raw SQL.
    """

    @staticmethod
    def create(email: str, password_hash: str, code: str, expires_at: float) -> None:
        """
        Inserts a new user record into the database.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, activation_code, code_expires_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (email, password_hash, code, expires_at),
                )

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user record from the database by their email address.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cur.fetchone()

    @staticmethod
    def set_active(email: str) -> None:
        """
        Updates a user's status to active in the database.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_active = TRUE WHERE email = %s", (email,)
                )
