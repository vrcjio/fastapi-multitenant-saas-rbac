import sqlite3
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.crud.crud_user import get_user_by_id
from app.schemas.token import TokenPayload
from app.schemas.user import UserResponse, UserRole

# Swagger UI /docs ke liye tokenUrl route define karna
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    conn: sqlite3.Connection = Depends(get_db)
) -> dict:
    """
    Decodes the JWT token, extracts user ID, and fetches the user from SQLite.
    Guarantees that the token is valid, non-expired, and matches an active user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    token_type: str = payload.get("type", "")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: Expected access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id: str = payload.get("sub")
    tenant_id: str = payload.get("tenant_id")
    
    if not user_id or not tenant_id:
        raise credentials_exception
        
    user = get_user_by_id(conn, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with token does not exist"
        )
        
    # Security Cross-Check: User ke DB tenant_id aur JWT tenant_id ka match hona lazmi hai
    if user["tenant_id"] != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant scope mismatch detected"
        )
        
    return user


def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verifies that the authenticated user account has not been deactivated.
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive user account"
        )
    return current_user


class RoleChecker:
    """
    Configurable dependency callable for Granular Role-Based Access Control (RBAC).
    Usage: Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = [r.value if isinstance(r, UserRole) else r for r in allowed_roles]

    def __call__(self, current_user: dict = Depends(get_current_active_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}"
            )
        return current_user


# Shorthand helper functions for route level injection
require_owner_or_admin = RoleChecker([UserRole.OWNER, UserRole.ADMIN])
require_owner_only = RoleChecker([UserRole.OWNER])