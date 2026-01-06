from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse,
    AssignUserToGroup, AssignRoleToGroup, AssignPermissionToGroup,
    GroupUserMappingResponse, GroupRoleMappingResponse, GroupPermissionMappingResponse
)
from app.schemas.user import UserResponse
from app.schemas.role import RoleResponse
from app.schemas.permission import PermissionResponse
from app.schemas.common import ResponseBase
from app.services.group_service import GroupService

router = APIRouter()

# ============ GROUP CRUD ============
@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db)
):
    """Create a new group"""
    group = GroupService.create_group(db, group_data)
    return group

@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get group by ID"""
    group = GroupService.get_group_by_id(db, group_id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group

@router.get("/", response_model=List[GroupResponse])
def list_groups(
    tenant_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all groups"""
    groups = GroupService.get_groups(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return groups

@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: UUID,
    group_data: GroupUpdate,
    db: Session = Depends(get_db)
):
    """Update group"""
    group = GroupService.update_group(db, group_id, group_data)
    return group

@router.delete("/{group_id}", response_model=ResponseBase)
def delete_group(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete group"""
    GroupService.delete_group(db, group_id)
    return ResponseBase(success=True, message="Group deleted successfully")


# ============ USER ASSIGNMENTS ============
@router.post("/assign-user", response_model=GroupUserMappingResponse, status_code=status.HTTP_201_CREATED)
def assign_user_to_group(
    assignment: AssignUserToGroup,
    db: Session = Depends(get_db)
):
    """Assign user to group"""
    mapping = GroupService.assign_user_to_group(
        db, 
        assignment.user_id, 
        assignment.group_id
    )
    return mapping

@router.delete("/remove-user/{group_id}/{user_id}", response_model=ResponseBase)
def remove_user_from_group(
    group_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove user from group"""
    GroupService.remove_user_from_group(db, user_id, group_id)
    return ResponseBase(success=True, message="User removed from group successfully")

@router.get("/{group_id}/users", response_model=List[UserResponse])
def get_group_users(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all users in a group"""
    users = GroupService.get_group_users(db, group_id)
    return users

@router.get("/user/{user_id}/groups", response_model=List[GroupResponse])
def get_user_groups(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all groups a user belongs to"""
    groups = GroupService.get_user_groups(db, user_id)
    return groups


# ============ ROLE ASSIGNMENTS ============
@router.post("/assign-role", response_model=GroupRoleMappingResponse, status_code=status.HTTP_201_CREATED)
def assign_role_to_group(
    assignment: AssignRoleToGroup,
    db: Session = Depends(get_db)
):
    """Assign role to group"""
    mapping = GroupService.assign_role_to_group(
        db,
        assignment.group_id,
        assignment.role_id
    )
    return mapping

@router.delete("/remove-role/{group_id}/{role_id}", response_model=ResponseBase)
def remove_role_from_group(
    group_id: UUID,
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove role from group"""
    GroupService.remove_role_from_group(db, group_id, role_id)
    return ResponseBase(success=True, message="Role removed from group successfully")

@router.get("/{group_id}/roles", response_model=List[RoleResponse])
def get_group_roles(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all roles assigned to a group"""
    roles = GroupService.get_group_roles(db, group_id)
    return roles


# ============ PERMISSION ASSIGNMENTS ============
@router.post("/assign-permission", response_model=GroupPermissionMappingResponse, status_code=status.HTTP_201_CREATED)
def assign_permission_to_group(
    assignment: AssignPermissionToGroup,
    db: Session = Depends(get_db)
):
    """Assign permission to group"""
    mapping = GroupService.assign_permission_to_group(
        db,
        assignment.group_id,
        assignment.permission_id
    )
    return mapping

@router.delete("/remove-permission/{group_id}/{permission_id}", response_model=ResponseBase)
def remove_permission_from_group(
    group_id: UUID,
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove permission from group"""
    GroupService.remove_permission_from_group(db, group_id, permission_id)
    return ResponseBase(success=True, message="Permission removed from group successfully")

@router.get("/{group_id}/permissions", response_model=List[PermissionResponse])
def get_group_permissions(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all permissions assigned to a group"""
    permissions = GroupService.get_group_permissions(db, group_id)
    return permissions