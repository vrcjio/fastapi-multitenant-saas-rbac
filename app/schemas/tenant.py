from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Acme Corp"])
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$", examples=["acme-corp"])


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: str
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)