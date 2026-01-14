"""
Pydantic schemas for data validation.
Defines the input and output structures for the User API.
"""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """
    Schema for user registration requests.
    Validates email format and password length.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    """
    Schema for user information responses.
    Used to return non-sensitive user data.
    """

    email: EmailStr
    is_active: bool


class ActivationRequest(BaseModel):
    """
    Schema for account activation requests.
    Requires the 4-digit code sent via email.
    """

    code: str
