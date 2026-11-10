from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    college_name: str = Field(min_length=2, max_length=180)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    college_name: str
    is_email_verified: bool
    is_admin: bool
    has_profile_picture: bool
    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
