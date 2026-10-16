import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud.crud_tenant import get_tenant_by_id
from app.schemas.tenant import TenantResponse

router = APIRouter(prefix="/tenants", tags=["Workspaces"])


@router.get("/current", response_model=TenantResponse)
def get_current_workspace_info(
    current_user: dict = Depends(get_current_active_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Fetch details of the workspace tenant for the logged-in user.
    """
    tenant = get_tenant_by_id(conn, tenant_id=current_user["tenant_id"])
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return tenant