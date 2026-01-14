"""
API Route handlers.
Defines the endpoints for user registration and account activation.
"""

import secrets
import logging
import time
from typing import Dict, Any
import smtplib
import psycopg
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic
from app.schemas.user import UserCreate, ActivationRequest
from app.models.user import UserRepo
from app.core.security import get_password_hash
from app.core.email import send_activation_email
from app.api.deps import get_current_active_user
from app.db import get_db_connection
from app.core.config import settings

router: APIRouter = APIRouter()
security: HTTPBasic = HTTPBasic()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate) -> Dict[str, str]:
    """
    Registers a new user, hashes their password, and sends an activation email.
    """
    logger.info("Registration attempt for email: %s", user_in.email)
    # Vérification asynchrone
    if await UserRepo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    code: str = str(secrets.randbelow(10000)).zfill(4)
    expires_at: float = time.time() + 60

    await UserRepo.create(
        user_in.email, get_password_hash(user_in.password), code, expires_at
    )

    # Send actual email asynchronously
    await send_activation_email(user_in.email, code)

    logger.info("New user registered: %s", user_in.email)
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
    email: str = str(current_user["email"])
    logger.info("Activation attempt for user: %s", email)

    # current_user is already verified for email/password by the dependency
    if current_user["is_active"]:
        logger.info("Activation skipped: User %s is already active", email)
        return {"message": "Already active"}

    if time.time() > float(current_user["code_expires_at"]):
        logger.warning("Activation failed: Code for %s has expired", email)
        raise HTTPException(status_code=400, detail="Code expired")

    if activation.code != str(current_user["activation_code"]):
        logger.warning("Activation failed: Invalid code provided for %s", email)
        raise HTTPException(status_code=400, detail="Invalid code")

    await UserRepo.set_active(str(current_user["email"]))
    logger.info("User account activated successfully: %s", email)
    return {"message": "Account activated successfully"}


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Checks the health of the application and its dependencies (DB and SMTP).
    Returns 503 if any dependency is unreachable.
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "dependencies": {"database": "unhealthy", "smtp": "unhealthy"},
    }

    # 1. Check Database
    try:
        async for conn in get_db_connection():
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                health_status["dependencies"]["database"] = "healthy"
    except (psycopg.Error, RuntimeError) as e:
        logger.error("Health check failed: Database unreachable. %s", e)
        health_status["status"] = "unhealthy"

    # 2. Check SMTP
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=3) as server:
            server.noop()
            health_status["dependencies"]["smtp"] = "healthy"
    except (smtplib.SMTPException, ConnectionError, TimeoutError) as e:
        logger.error("Health check failed: SMTP server unreachable. %s", e)
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status
