from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.models.user import UserRepo
from app.core.security import verify_password

security = HTTPBasic()

def get_current_active_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Dependency to get the user from the database and verify credentials.
    Returns the user dictionary if valid.
    """
    user = UserRepo.get_by_email(credentials.username)
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user

def get_current_user_email(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Simpler dependency if you only need the email from the credentials
    without necessarily querying the DB (though Basic Auth usually requires it).
    """
    return credentials.username
