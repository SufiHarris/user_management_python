from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.common import TimestampMixin

class GroupBase(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class GroupCreate(GroupBase):
    tenant_id: UUID

class GroupUpdate(BaseModel):
    group_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class GroupResponse(GroupBase, TimestampMixin):
    group_id: UUID
    tenant_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# Group Assignment Schemas
class AssignUserToGroup(BaseModel):
    user_id: UUID
    group_id: UUID

class AssignRoleToGroup(BaseModel):
    group_id: UUID
    role_id: UUID

class AssignPermissionToGroup(BaseModel):
    group_id: UUID
    permission_id: UUID

class GroupUserMappingResponse(BaseModel):
    id: UUID
    group_id: UUID
    user_id: UUID
    assigned_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GroupRoleMappingResponse(BaseModel):
    id: UUID
    group_id: UUID
    role_id: UUID
    assigned_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GroupPermissionMappingResponse(BaseModel):
    id: UUID
    group_id: UUID
    permission_id: UUID
    assigned_at: datetime
    
    model_config = ConfigDict(from_attributes=True)