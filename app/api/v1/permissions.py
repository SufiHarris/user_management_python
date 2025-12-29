from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.permission import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    AssignPermissionToUser, AssignPermissionToRole
)
from app.schemas.common import ResponseBase
from app.services.permission_service import PermissionService

router = APIRouter()

@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    permission = PermissionService.create_permission(db, permission_data)
    return permission

@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Get permission by ID"""
    permission = PermissionService.get_permission_by_id(db, permission_id)
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission

@router.get("/", response_model=List[PermissionResponse])
def list_permissions(
    resource: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all permissions"""
    permissions = PermissionService.get_permissions(db, resource=resource, skip=skip, limit=limit)
    return permissions

@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: UUID,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db)
):
    """Update permission"""
    permission = PermissionService.update_permission(db, permission_id, permission_data)
    return permission

@router.delete("/{permission_id}", response_model=ResponseBase)
def delete_permission(
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete permission"""
    PermissionService.delete_permission(db, permission_id)
    return ResponseBase(success=True, message="Permission deleted successfully")

@router.post("/assign-user", response_model=ResponseBase, status_code=status.HTTP_201_CREATED)
def assign_permission_to_user(
    assignment: AssignPermissionToUser,
    db: Session = Depends(get_db)
):
    """Assign permission directly to user"""
    PermissionService.assign_permission_to_user(
        db,
        assignment.user_id,
        assignment.permission_id
    )
    return ResponseBase(success=True, message="Permission assigned to user successfully")

@router.post("/assign-role", response_model=ResponseBase, status_code=status.HTTP_201_CREATED)
def assign_permission_to_role(
    assignment: AssignPermissionToRole,
    db: Session = Depends(get_db)
):
    """Assign permission to role"""
    PermissionService.assign_permission_to_role(
        db,
        assignment.role_id,
        assignment.permission_id
    )
    return ResponseBase(success=True, message="Permission assigned to role successfully")

@router.get("/user/{user_id}/permissions", response_model=List[PermissionResponse])
def get_user_permissions(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all permissions for a user (direct + through roles)"""
    permissions = PermissionService.get_user_permissions(db, user_id)
    return permissions