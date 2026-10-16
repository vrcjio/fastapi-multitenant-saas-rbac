import sqlite3
import uuid
from typing import Optional
from app.schemas.tenant import TenantCreate


def create_tenant(conn: sqlite3.Connection, tenant_in: TenantCreate) -> dict:
    tenant_id = str(uuid.uuid4())
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tenants (id, name, slug, is_active)
        VALUES (?, ?, ?, 1)
        """,
        (tenant_id, tenant_in.name, tenant_in.slug.lower())
    )
    conn.commit()
    return get_tenant_by_id(conn, tenant_id)


def get_tenant_by_id(conn: sqlite3.Connection, tenant_id: str) -> Optional[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_tenant_by_slug(conn: sqlite3.Connection, slug: str) -> Optional[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE slug = ?", (slug.lower(),))
    row = cursor.fetchone()
    return dict(row) if row else None