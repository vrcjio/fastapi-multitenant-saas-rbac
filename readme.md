# 🏢 Multi-Tenant SaaS Workspace & RBAC Engine

A production-grade, modular B2B SaaS backend template built with **FastAPI**, **SQLite3**, **Pydantic V2**, and **JWT**. Designed to demonstrate real-world enterprise architectures including tenant data isolation, granular Role-Based Access Control (RBAC), and token rotation.

---

## ⚡ Highlights

- **Multi-Tenant Isolation:** Strict tenant scoping (`UNIQUE(tenant_id, email)`) preventing cross-organization data leakage.
- **Granular RBAC Engine:** Declarative dependency injection enforcing permissions across `OWNER`, `ADMIN`, and `MEMBER` roles.
- **Enterprise Security:** Bcrypt salted password hashing with OAuth2 compliant JWT Access & Refresh token rotation.
- **Type-Safe Validation:** Full Pydantic V2 schema serialization and custom slug pattern enforcement.
- **Pure Python Stack:** Built using Python's native SQLite with foreign key enforcement and connection lifecycles.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.10+
- **Database:** SQLite3 (WAL mode, Foreign Keys enabled)
- **Validation:** Pydantic V2, Pydantic-Settings
- **Security:** PyJWT, Bcrypt, Python-Multipart
- **Server:** Uvicorn (ASGI)