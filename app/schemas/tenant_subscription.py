from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from uuid import UUID

class TenantSubscriptionBase(BaseModel):
    tenant_id: UUID
    module_id: UUID
    subscription_start_date: Optional[date] = None
    subscription_end_date: Optional[date] = None

class TenantSubscriptionCreate(TenantSubscriptionBase):
    pass

class TenantSubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None
    subscription_start_date: Optional[date] = None
    subscription_end_date: Optional[date] = None

class TenantSubscriptionResponse(TenantSubscriptionBase):
    subscription_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)