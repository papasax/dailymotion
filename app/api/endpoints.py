import secrets
import time
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.schemas.user import UserCreate, ActivationRequest, UserResponse
from app.models.user import UserRepo
from app.core.security import verify_password, get_password_hash
from app.core.email import send_activation_email
from app.api.deps import get_current_active_user

router = APIRouter()
security = HTTPBasic()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    if UserRepo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    code = str(secrets.randbelow(10000)).zfill(4)
    expires_at = time.time() + 60
    
    UserRepo.create(user_in.email, get_password_hash(user_in.password), code, expires_at)
    
    # Send actual email
    send_activation_email(user_in.email, code)
    
    return {"message": "User registered. Please check your email for the code."}

@router.post("/activate")
async def activate(
    activation: ActivationRequest, 
    current_user: dict = Depends(get_current_active_user)
):
    # current_user is already verified for email/password by the dependency
    if current_user["is_active"]:
        return {"message": "Already active"}
        
    if time.time() > current_user["code_expires_at"]:
        raise HTTPException(status_code=400, detail="Code expired")
    
    if activation.code != current_user["activation_code"]:
        raise HTTPException(status_code=400, detail="Invalid code")

    UserRepo.set_active(current_user["email"])
    return {"message": "Account activated successfully"}
