"""
API Dependencies.
Contains reusable dependencies for authentication and request processing.
"""

from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.models.user import UserRepo
from app.core.security import verify_password

security = HTTPBasic()


async def get_current_active_user(
    credentials: HTTPBasicCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency to get the user from the database and verify credentials.
    Returns the user dictionary if valid.
    """
    # Appel asynchrone au repository
    user = await UserRepo.get_by_email(credentials.username)

    if not user or not verify_password(
        credentials.password, str(user["password_hash"])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user
