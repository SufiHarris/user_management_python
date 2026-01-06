from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.common import TimestampMixin

class RoleBase(BaseModel):
    role_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class RoleCreate(RoleBase):
    tenant_id: UUID
    is_system_role: bool = False

class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None  # Added

class RoleResponse(RoleBase, TimestampMixin):
    role_id: UUID
    tenant_id: UUID
    is_system_role: bool
    is_active: bool  # Added
    
    model_config = ConfigDict(from_attributes=True)

# Role Assignment Schemas
class AssignRoleToUser(BaseModel):
    user_id: UUID
    role_id: UUID

class AssignRoleToGroup(BaseModel):
    group_id: UUID
    role_id: UUID

class UserRoleMappingResponse(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    is_active: bool # Added to see status
    assigned_at: datetime
    
    model_config = ConfigDict(from_attributes=True)