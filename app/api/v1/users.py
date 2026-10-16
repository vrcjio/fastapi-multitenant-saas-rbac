import sqlite3
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_owner_or_admin, get_current_active_user
from app.core.database import get_db
from app.crud.crud_user import create_user, get_user_by_email_and_tenant, get_users_by_tenant
from app.schemas.user import UserCreate, UserResponse, UserRole

router = APIRouter(prefix="/users", tags=["Users & Team Management"])


@router.get("/", response_model=List[UserResponse])
def list_workspace_users(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    List all team members inside the current tenant workspace.
    Guaranteed multi-tenant isolation: Scoped strictly to current_user['tenant_id'].
    """
    users = get_users_by_tenant(
        conn, 
        tenant_id=current_user["tenant_id"], 
        limit=limit, 
        offset=skip
    )
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def invite_user_to_workspace(
    user_in: UserCreate,
    current_admin: dict = Depends(require_owner_or_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Invite/Create a new user in the workspace.
    RBAC Protected: Only OWNER or ADMIN can invoke this endpoint.
    """
    # Prevent ADMIN from creating an OWNER
    if current_admin["role"] == UserRole.ADMIN.value and user_in.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot assign the OWNER role"
        )

    existing_user = get_user_by_email_and_tenant(
        conn, 
        email=user_in.email, 
        tenant_id=current_admin["tenant_id"]
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists in this workspace"
        )

    new_user = create_user(
        conn, 
        user_in=user_in, 
        tenant_id=current_admin["tenant_id"], 
        role=user_in.role
    )
    return new_user