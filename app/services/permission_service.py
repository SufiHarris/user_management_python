from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.permission import PermissionMaster, PermissionUserMapping, GroupPermissionMapping
from app.models.role import RolePermissionMapping, RoleMaster
from app.models.user import UserDetails
from app.models.group import GroupMaster
from app.schemas.permission import PermissionCreate, PermissionUpdate

class PermissionService:
    @staticmethod
    def create_permission(db: Session, permission_data: PermissionCreate) -> PermissionMaster:
        """Create a new permission"""
        try:
            db_permission = PermissionMaster(
                permission_name=permission_data.permission_name,
                resource=permission_data.resource,
                action=permission_data.action,
                description=permission_data.description
            )
            
            db.add(db_permission)
            db.commit()
            db.refresh(db_permission)
            
            return db_permission
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission with this name or resource-action combination already exists"
            )
    
    @staticmethod
    def get_permission_by_id(db: Session, permission_id: UUID) -> Optional[PermissionMaster]:
        """Get permission by ID"""
        return db.query(PermissionMaster).filter(
            PermissionMaster.permission_id == permission_id
        ).first()
    
    @staticmethod
    def get_permissions(db: Session, resource: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[PermissionMaster]:
        """Get list of permissions"""
        query = db.query(PermissionMaster)
        
        if resource:
            query = query.filter(PermissionMaster.resource == resource)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_permission(db: Session, permission_id: UUID, permission_data: PermissionUpdate) -> PermissionMaster:
        """Update permission"""
        db_permission = db.query(PermissionMaster).filter(
            PermissionMaster.permission_id == permission_id
        ).first()
        
        if not db_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        update_data = permission_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_permission, field, value)
        
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def delete_permission(db: Session, permission_id: UUID) -> bool:
        """Delete permission"""
        db_permission = db.query(PermissionMaster).filter(
            PermissionMaster.permission_id == permission_id
        ).first()
        
        if not db_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        db.delete(db_permission)
        db.commit()
        return True
    
    @staticmethod
    def assign_permission_to_user(db: Session, user_id: UUID, permission_id: UUID, assigned_by: Optional[UUID] = None) -> PermissionUserMapping:
        """Assign permission directly to user"""
        # Verify user exists
        user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify permission exists
        permission = db.query(PermissionMaster).filter(
            PermissionMaster.permission_id == permission_id
        ).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Check if already assigned
        existing = db.query(PermissionUserMapping).filter(
            PermissionUserMapping.user_id == user_id,
            PermissionUserMapping.permission_id == permission_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already assigned to user"
            )
        
        try:
            mapping = PermissionUserMapping(
                user_id=user_id,
                permission_id=permission_id,
                assigned_by=assigned_by
            )
            
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
            
            return mapping
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign permission"
            )
    
    @staticmethod
    def assign_permission_to_role(db: Session, role_id: UUID, permission_id: UUID) -> RolePermissionMapping:
        """Assign permission to role"""
        # Verify role exists
        role = db.query(RoleMaster).filter(RoleMaster.role_id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Verify permission exists
        permission = db.query(PermissionMaster).filter(
            PermissionMaster.permission_id == permission_id
        ).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Check if already assigned
        existing = db.query(RolePermissionMapping).filter(
            RolePermissionMapping.role_id == role_id,
            RolePermissionMapping.permission_id == permission_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already assigned to role"
            )
        
        try:
            mapping = RolePermissionMapping(
                role_id=role_id,
                permission_id=permission_id
            )
            
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
            
            return mapping
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign permission to role"
            )
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: UUID) -> List[PermissionMaster]:
        """Get all permissions for a user (direct + through roles + through groups)"""
        # Direct permissions
        direct_perms = db.query(PermissionMaster).join(
            PermissionUserMapping, 
            PermissionUserMapping.permission_id == PermissionMaster.permission_id
        ).filter(
            PermissionUserMapping.user_id == user_id
        ).all()
        
        # Permissions through roles
        role_perms = db.query(PermissionMaster).join(
            RolePermissionMapping,
            RolePermissionMapping.permission_id == PermissionMaster.permission_id
        ).join(
            UserRoleMapping,
            UserRoleMapping.role_id == RolePermissionMapping.role_id
        ).filter(
            UserRoleMapping.user_id == user_id
        ).all()
        
        # Combine and deduplicate
        all_perms = {perm.permission_id: perm for perm in direct_perms + role_perms}
        return list(all_perms.values())