import sqlite3
import uuid
from typing import List, Optional
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserRole


def create_user(
    conn: sqlite3.Connection, 
    user_in: UserCreate, 
    tenant_id: str, 
    role: UserRole = UserRole.MEMBER
) -> dict:
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_in.password)
    
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (id, tenant_id, email, hashed_password, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (user_id, tenant_id, user_in.email.lower(), hashed_password, user_in.full_name, role.value)
    )
    conn.commit()
    return get_user_by_id(conn, user_id)


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> Optional[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_email_and_tenant(
    conn: sqlite3.Connection, 
    email: str, 
    tenant_id: str
) -> Optional[dict]:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND tenant_id = ?",
        (email.lower(), tenant_id)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def get_users_by_tenant(
    conn: sqlite3.Connection, 
    tenant_id: str, 
    limit: int = 50, 
    offset: int = 0
) -> List[dict]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, tenant_id, email, full_name, role, is_active, created_at 
        FROM users 
        WHERE tenant_id = ? 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
        """,
        (tenant_id, limit, offset)
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]