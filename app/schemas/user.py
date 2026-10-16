from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    workspace_name: str = Field(..., min_length=2, max_length=100)
    workspace_slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")


class UserCreate(UserBase):
    """Admin dwara naye team member ko add karne ke liye schema."""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.MEMBER


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str


class UserResponse(UserBase):
    id: str
    tenant_id: str
    role: UserRole
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)