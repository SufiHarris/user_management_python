from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from app.schemas.common import TimestampMixin

class TenantBase(BaseModel):
    tenant_name: str = Field(..., min_length=1, max_length=255)

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    tenant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class TenantResponse(TenantBase, TimestampMixin):
    tenant_id: UUID
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)