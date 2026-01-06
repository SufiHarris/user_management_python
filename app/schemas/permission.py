from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.common import TimestampMixin

class PermissionBase(BaseModel):
    permission_name: str = Field(..., min_length=1, max_length=100)
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = Field(None, min_length=1, max_length=100)
    resource: Optional[str] = Field(None, min_length=1, max_length=100)
    action: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PermissionResponse(PermissionBase, TimestampMixin):
    permission_id: UUID
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# Permission Assignment Schemas
class AssignPermissionToUser(BaseModel):
    user_id: UUID
    permission_id: UUID

class AssignPermissionToRole(BaseModel):
    role_id: UUID
    permission_id: UUID

class AssignPermissionToGroup(BaseModel):
    group_id: UUID
    permission_id: UUID