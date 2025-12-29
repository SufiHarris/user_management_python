from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class PermissionBase(BaseModel):
    permission_name: str = Field(..., min_length=1, max_length=100)
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    permission_id: UUID
    created_at: datetime
    
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