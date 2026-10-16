# Project Blueprint: Multi-Tenant RBAC Workspace API

---

## 1. Project Overview & Pitch
**Title:** Multi-Tenant Role-Based Access Control (RBAC) Workspace Engine  
**Tech Stack:** Python 3.10+, FastAPI, Pydantic V2, SQLite3 / aiosqlite, PyJWT, Passlib (Bcrypt)  

### Resume Headline:
> *"Architected and deployed an enterprise-grade multi-tenant workspace platform using FastAPI, featuring granular Role-Based Access Control (RBAC), JWT token rotation, custom dependency injection filters, and tenant-isolated data access layers."*

---

## 2. Core Architectural Concepts

1. **Multi-Tenancy (Data Isolation):**
   * Har user ek ya multiple **Organizations/Workspaces** ka part ho sakta hai.
   * Har query me `workspace_id` automatically validate aur filter hoti hai, jisse ek tenant ka data doosra tenant kisi bhi haal me access na kar sake (Preventing IDOR vulnerabilities).

2. **Hierarchical RBAC (Permissions):**
   * **Owner:** Organization create karta hai, members invite/remove karta hai, billing/settings update karta hai.
   * **Admin:** Projects/Tasks create karta hai, members assign karta hai.
   * **Member:** Assigned tasks/projects create aur update kar sakta hai.
   * **Viewer:** Read-only access.

3. **Secure Authentication Flow:**
   * **Access Token:** Short-lived (15–30 minutes) JWT bearer token.
   * **Refresh Token:** Long-lived (7 days) token stored safely to rotate tokens without requiring re-login.
   * Password hashing via `bcrypt` with automated salt generation.

---

## 3. Database Schema (SQLite3 Design)

```sql
-- 1. Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Workspaces (Tenants)
CREATE TABLE workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    owner_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- 3. Workspace Memberships (Junction table with Roles)
CREATE TABLE workspace_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT CHECK(role IN ('owner', 'admin', 'member', 'viewer')) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, user_id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Projects (Tenant-Scoped Resource)
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 5. Tasks (Scoped to Projects & Workspaces)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    workspace_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('todo', 'in_progress', 'done')) DEFAULT 'todo',
    assigned_to INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);
```

---

## 4. Production-Ready Folder Structure

```text
workspace_saas_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI initialization, middleware, routes inclusion
│   │
│   ├── core/                    # Global configs, security, constants
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic BaseSettings (ENV loader)
│   │   ├── security.py          # Password hashing, JWT token generation/verification
│   │   └── dependencies.py      # Dependency injection (current_user, check_permissions)
│   │
│   ├── db/                      # Database connection and utilities
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite connection manager, row factory
│   │   └── init_db.py           # DDL execution & seed script
│   │
│   ├── schemas/                 # Pydantic validation schemas (V2)
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, Token, Refresh schemas
│   │   ├── user.py              # UserCreate, UserResponse
│   │   ├── workspace.py         # WorkspaceCreate, MemberInvite, WorkspaceOut
│   │   ├── project.py           # ProjectCreate, ProjectResponse
│   │   └── task.py              # TaskCreate, TaskUpdate, TaskResponse
│   │
│   ├── repositories/            # Direct DB queries (Clean separation from routes)
│   │   ├── __init__.py
│   │   ├── user_repo.py
│   │   ├── workspace_repo.py
│   │   ├── project_repo.py
│   │   └── task_repo.py
│   │
│   └── routers/                 # API endpoints
│       ├── __init__.py
│       ├── auth.py              # /api/v1/auth (signup, login, refresh)
│       ├── users.py             # /api/v1/users (profile, update)
│       ├── workspaces.py        # /api/v1/workspaces (CRUD, invite, roles)
│       ├── projects.py          # /api/v1/workspaces/{w_id}/projects
│       └── tasks.py             # /api/v1/workspaces/{w_id}/projects/{p_id}/tasks
│
├── tests/                       # Pytest unit & integration tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_auth.py
│
├── .env.example                 # Environment variables sample
├── .gitignore                   # Ignores .venv, .db, __pycache__
├── README.md                    # Project documentation for recruiters
└── requirements.txt             # Dependency list
```

---

## 5. Step-by-Step Environment Setup Guide

### Step 1: Directory Setup & Virtual Environment
Terminal me ye commands run karein:

```bash
# Project directory banayein aur enter karein
mkdir workspace_saas_api
cd workspace_saas_api

# Python virtual environment create karein
python -m venv venv

# Virtual environment activate karein
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

---

### Step 2: `requirements.txt` File

```text
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
```

Install karne ke liye:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: `.env.example` File

```ini
APP_NAME="Multi-Tenant Workspace API"
ENVIRONMENT="development"
SECRET_KEY="replace-this-with-a-very-long-random-secret-key-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_PATH="saas_workspace.db"
```

---

## 6. Next Implementation Milestones

1. **Phase 1 (Foundation):** `core/config.py` setup, SQLite connection manager, aur database auto-initialization script.
2. **Phase 2 (Security):** `core/security.py` me Bcrypt hashing aur JWT access/refresh token generation.
3. **Phase 3 (Auth Routers):** User Registration, Login endpoint, aur Dependency Injection se protected `/me` endpoint.
4. **Phase 4 (Tenancy & RBAC):** Workspace creation, membership verification decorator/dependency (`RoleChecker`).
5. **Phase 5 (Business CRUD):** Projects aur Tasks management with workspace isolation filters.