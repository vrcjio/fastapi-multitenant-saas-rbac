import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password
)
from app.crud.crud_tenant import create_tenant, get_tenant_by_slug
from app.crud.crud_user import (
    create_user,
    get_user_by_email_and_tenant,
    get_user_by_id
)
from app.api.deps import get_current_active_user
from app.schemas.tenant import TenantCreate
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserRegister, UserResponse, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_workspace(
    user_in: UserRegister, 
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Onboard a new company/tenant workspace and create the initial OWNER account.
    """
    existing_tenant = get_tenant_by_slug(conn, user_in.workspace_slug)
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace slug already exists. Please pick another."
        )

    # 1. Create Workspace
    tenant = create_tenant(
        conn, 
        TenantCreate(name=user_in.workspace_name, slug=user_in.workspace_slug)
    )

    # 2. Create Owner User
    user_create_data = UserCreate(
        email=user_in.email,
        full_name=user_in.full_name,
        password=user_in.password,
        role=UserRole.OWNER
    )
    new_user = create_user(
        conn, 
        user_in=user_create_data, 
        tenant_id=tenant["id"], 
        role=UserRole.OWNER
    )
    return new_user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    OAuth2 compatible token login. 
    Format username as 'email@domain.com::workspace-slug' OR provide direct tenant match.
    """
    username_raw = form_data.username
    if "::" in username_raw:
        email, tenant_slug = username_raw.split("::", 1)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be formatted as 'email::workspace-slug' for multi-tenant login."
        )

    tenant = get_tenant_by_slug(conn, tenant_slug)
    if not tenant or not tenant["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant workspace or workspace is inactive."
        )

    user = get_user_by_email_and_tenant(conn, email=email, tenant_id=tenant["id"])
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, password, or tenant credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")

    access_token = create_access_token(
        user_id=user["id"], 
        tenant_id=tenant["id"], 
        role=user["role"]
    )
    refresh_token = create_refresh_token(
        user_id=user["id"], 
        tenant_id=tenant["id"], 
        role=user["role"]
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    token_in: RefreshTokenRequest,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Issues a fresh Access Token using a valid Refresh Token.
    """
    payload = decode_token(token_in.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = get_user_by_id(conn, payload.get("sub"))
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer active or exists"
        )

    new_access_token = create_access_token(
        user_id=user["id"],
        tenant_id=user["tenant_id"],
        role=user["role"]
    )
    new_refresh_token = create_refresh_token(
        user_id=user["id"],
        tenant_id=user["tenant_id"],
        role=user["role"]
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def read_current_user_profile(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Returns authenticated user's profile details.
    """
    return current_user