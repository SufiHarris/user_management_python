from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse,
    AssignRoleToUser, UserRoleMappingResponse
)
from app.schemas.permission import PermissionResponse
from app.schemas.common import ResponseBase
from app.services.role_service import RoleService

router = APIRouter()

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db)
):
    """Create a new role"""
    role = RoleService.create_role(db, role_data)
    return role

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Get role by ID"""
    role = RoleService.get_role_by_id(db, role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role

@router.get("/", response_model=List[RoleResponse])
def list_roles(
    tenant_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all roles"""
    roles = RoleService.get_roles(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return roles

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    db: Session = Depends(get_db)
):
    """Update role"""
    role = RoleService.update_role(db, role_id, role_data)
    return role

@router.delete("/{role_id}", response_model=ResponseBase)
def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete role"""
    RoleService.delete_role(db, role_id)
    return ResponseBase(success=True, message="Role deleted successfully")

@router.post("/assign-user", response_model=UserRoleMappingResponse, status_code=status.HTTP_201_CREATED)
def assign_role_to_user(
    assignment: AssignRoleToUser,
    db: Session = Depends(get_db)
):
    """Assign role to user"""
    mapping = RoleService.assign_role_to_user(
        db, 
        assignment.user_id, 
        assignment.role_id
    )
    return mapping

@router.delete("/remove-user/{user_id}/{role_id}", response_model=ResponseBase)
def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove role from user"""
    RoleService.remove_role_from_user(db, user_id, role_id)
    return ResponseBase(success=True, message="Role removed from user successfully")

@router.get("/user/{user_id}/roles", response_model=List[RoleResponse])
def get_user_roles(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all roles for a user"""
    roles = RoleService.get_user_roles(db, user_id)
    return roles