"""
Security utilities.
Handles password hashing and verification using Bcrypt.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a salted Bcrypt hash.
    Truncates input to 72 bytes for Bcrypt compatibility.
    """
    # Truncate to 72 bytes to prevent bcrypt ValueError for long strings
    return pwd_context.verify(plain_password[:72], hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a salted Bcrypt hash from a plain text password.
    Truncates input to 72 bytes for Bcrypt compatibility.
    """
    # Truncate to 72 bytes to prevent bcrypt ValueError for long strings
    return pwd_context.hash(password[:72])
