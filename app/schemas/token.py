from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str          # User ID
    tenant_id: str    # Multi-tenant scoping ke liye
    role: str         # RBAC verification ke liye
    exp: Optional[int] = None
    type: str         # 'access' ya 'refresh'


class RefreshTokenRequest(BaseModel):
    refresh_token: str