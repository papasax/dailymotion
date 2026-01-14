"""
API Route handlers.
Defines the endpoints for user registration and account activation.
"""

import secrets
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic
from app.schemas.user import UserCreate, ActivationRequest
from app.models.user import UserRepo
from app.core.security import get_password_hash
from app.core.email import send_activation_email
from app.api.deps import get_current_active_user

router: APIRouter = APIRouter()
security: HTTPBasic = HTTPBasic()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate) -> Dict[str, str]:
    """
    Registers a new user, hashes their password, and sends an activation email.
    """
    if UserRepo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    code: str = str(secrets.randbelow(10000)).zfill(4)
    expires_at: float = time.time() + 60

    UserRepo.create(
        user_in.email, get_password_hash(user_in.password), code, expires_at
    )

    # Send actual email
    send_activation_email(user_in.email, code)

    return {"message": "User registered. Please check your email for the code."}


@router.post("/activate")
async def activate(
    activation: ActivationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Activates a user account if the provided code matches and has not expired.
    Requires Basic Authentication.
    """
    # current_user is already verified for email/password by the dependency
    if current_user["is_active"]:
        return {"message": "Already active"}

    if time.time() > float(current_user["code_expires_at"]):
        raise HTTPException(status_code=400, detail="Code expired")

    if activation.code != str(current_user["activation_code"]):
        raise HTTPException(status_code=400, detail="Invalid code")

    UserRepo.set_active(str(current_user["email"]))
    return {"message": "Account activated successfully"}
