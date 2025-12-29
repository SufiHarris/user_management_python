from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.role import RoleMaster, UserRoleMapping, RolePermissionMapping
from app.models.user import UserDetails
from app.models.permission import PermissionMaster
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> RoleMaster:
        """Create a new role"""
        try:
            db_role = RoleMaster(
                tenant_id=role_data.tenant_id,
                role_name=role_data.role_name,
                description=role_data.description,
                is_system_role=role_data.is_system_role
            )
            
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            
            return db_role
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists for this tenant"
            )
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: UUID) -> Optional[RoleMaster]:
        """Get role by ID"""
        return db.query(RoleMaster).filter(RoleMaster.role_id == role_id).first()
    
    @staticmethod
    def get_roles(db: Session, tenant_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[RoleMaster]:
        """Get list of roles"""
        query = db.query(RoleMaster)
        
        if tenant_id:
            query = query.filter(RoleMaster.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_role(db: Session, role_id: UUID, role_data: RoleUpdate) -> RoleMaster:
        """Update role"""
        db_role = db.query(RoleMaster).filter(RoleMaster.role_id == role_id).first()
        
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if db_role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify system role"
            )
        
        update_data = role_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        try:
            db.commit()
            db.refresh(db_role)
            return db_role
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed due to database constraint"
            )
    
    @staticmethod
    def delete_role(db: Session, role_id: UUID) -> bool:
        """Delete role"""
        db_role = db.query(RoleMaster).filter(RoleMaster.role_id == role_id).first()
        
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if db_role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete system role"
            )
        
        db.delete(db_role)
        db.commit()
        return True
    
    @staticmethod
    def assign_role_to_user(db: Session, user_id: UUID, role_id: UUID, assigned_by: Optional[UUID] = None) -> UserRoleMapping:
        """Assign role to user"""
        # Check if user exists
        user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if role exists
        role = db.query(RoleMaster).filter(RoleMaster.role_id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if user and role belong to same tenant
        if user.tenant_id != role.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User and role must belong to the same tenant"
            )
        
        # Check if already assigned
        existing = db.query(UserRoleMapping).filter(
            UserRoleMapping.user_id == user_id,
            UserRoleMapping.role_id == role_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already assigned to user"
            )
        
        try:
            mapping = UserRoleMapping(
                user_id=user_id,
                role_id=role_id,
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
                detail="Failed to assign role"
            )
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: UUID, role_id: UUID) -> bool:
        """Remove role from user"""
        mapping = db.query(UserRoleMapping).filter(
            UserRoleMapping.user_id == user_id,
            UserRoleMapping.role_id == role_id
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )
        
        db.delete(mapping)
        db.commit()
        return True
    
    @staticmethod
    def get_user_roles(db: Session, user_id: UUID) -> List[RoleMaster]:
        """Get all roles assigned to a user"""
        return db.query(RoleMaster).join(
            UserRoleMapping, UserRoleMapping.role_id == RoleMaster.role_id
        ).filter(
            UserRoleMapping.user_id == user_id
        ).all()