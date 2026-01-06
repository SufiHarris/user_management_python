from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.group import GroupMaster, GroupUserMapping
from app.models.role import GroupRoleMapping, RoleMaster
from app.models.permission import GroupPermissionMapping, PermissionMaster
from app.models.user import UserDetails
from app.models.tenant import TenantMaster
from app.schemas.group import GroupCreate, GroupUpdate

class GroupService:
    @staticmethod
    def create_group(db: Session, group_data: GroupCreate) -> GroupMaster:
        """Create a new group"""
        # Check if tenant exists
        tenant = db.query(TenantMaster).filter(TenantMaster.tenant_id == group_data.tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        try:
            db_group = GroupMaster(
                tenant_id=group_data.tenant_id,
                group_name=group_data.group_name,
                description=group_data.description
            )
            
            db.add(db_group)
            db.commit()
            db.refresh(db_group)
            
            return db_group
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group with this name already exists for this tenant"
            )
    
    @staticmethod
    def get_group_by_id(db: Session, group_id: UUID) -> Optional[GroupMaster]:
        """Get group by ID"""
        return db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
    
    @staticmethod
    def get_groups(db: Session, tenant_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[GroupMaster]:
        """Get list of groups"""
        query = db.query(GroupMaster)
        
        if tenant_id:
            query = query.filter(GroupMaster.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_group(db: Session, group_id: UUID, group_data: GroupUpdate) -> GroupMaster:
        """Update group"""
        db_group = db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
        
        if not db_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        update_data = group_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_group, field, value)
        
        try:
            db.commit()
            db.refresh(db_group)
            return db_group
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed due to database constraint"
            )
    
    @staticmethod
    def delete_group(db: Session, group_id: UUID) -> bool:
        """Delete group"""
        db_group = db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
        
        if not db_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        db.delete(db_group)
        db.commit()
        return True
    
    # ============ USER MAPPINGS ============
    @staticmethod
    def assign_user_to_group(db: Session, user_id: UUID, group_id: UUID) -> GroupUserMapping:
        """Assign user to group"""
        # Check if user exists
        user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if group exists
        group = db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if user and group belong to same tenant
        if user.tenant_id != group.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User and group must belong to the same tenant"
            )
        
        # Check if already assigned
        existing = db.query(GroupUserMapping).filter(
            GroupUserMapping.user_id == user_id,
            GroupUserMapping.group_id == group_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already assigned to group"
            )
        
        try:
            mapping = GroupUserMapping(
                user_id=user_id,
                group_id=group_id
            )
            
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
            
            return mapping
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign user to group"
            )
    
    @staticmethod
    def remove_user_from_group(db: Session, user_id: UUID, group_id: UUID) -> bool:
        """Remove user from group"""
        mapping = db.query(GroupUserMapping).filter(
            GroupUserMapping.user_id == user_id,
            GroupUserMapping.group_id == group_id
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in group"
            )
        
        db.delete(mapping)
        db.commit()
        return True
    
    @staticmethod
    def get_group_users(db: Session, group_id: UUID) -> List[UserDetails]:
        """Get all users in a group"""
        mappings = db.query(GroupUserMapping).filter(GroupUserMapping.group_id == group_id).all()
        user_ids = [m.user_id for m in mappings]
        users = db.query(UserDetails).filter(UserDetails.user_id.in_(user_ids)).all()
        return users
    
    @staticmethod
    def get_user_groups(db: Session, user_id: UUID) -> List[GroupMaster]:
        """Get all groups a user belongs to"""
        mappings = db.query(GroupUserMapping).filter(GroupUserMapping.user_id == user_id).all()
        group_ids = [m.group_id for m in mappings]
        groups = db.query(GroupMaster).filter(GroupMaster.group_id.in_(group_ids)).all()
        return groups
    
    # ============ ROLE MAPPINGS ============
    @staticmethod
    def assign_role_to_group(db: Session, group_id: UUID, role_id: UUID) -> GroupRoleMapping:
        """Assign role to group"""
        # Check if group exists
        group = db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if role exists
        role = db.query(RoleMaster).filter(RoleMaster.role_id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if group and role belong to same tenant
        if group.tenant_id != role.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group and role must belong to the same tenant"
            )
        
        # Check if already assigned
        existing = db.query(GroupRoleMapping).filter(
            GroupRoleMapping.group_id == group_id,
            GroupRoleMapping.role_id == role_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already assigned to group"
            )
        
        try:
            mapping = GroupRoleMapping(
                group_id=group_id,
                role_id=role_id
            )
            
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
            
            return mapping
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign role to group"
            )
    
    @staticmethod
    def remove_role_from_group(db: Session, group_id: UUID, role_id: UUID) -> bool:
        """Remove role from group"""
        mapping = db.query(GroupRoleMapping).filter(
            GroupRoleMapping.group_id == group_id,
            GroupRoleMapping.role_id == role_id
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found in group"
            )
        
        db.delete(mapping)
        db.commit()
        return True
    
    @staticmethod
    def get_group_roles(db: Session, group_id: UUID) -> List[RoleMaster]:
        """Get all roles assigned to a group"""
        mappings = db.query(GroupRoleMapping).filter(GroupRoleMapping.group_id == group_id).all()
        role_ids = [m.role_id for m in mappings]
        roles = db.query(RoleMaster).filter(RoleMaster.role_id.in_(role_ids)).all()
        return roles
    
    # ============ PERMISSION MAPPINGS ============
    @staticmethod
    def assign_permission_to_group(db: Session, group_id: UUID, permission_id: UUID) -> GroupPermissionMapping:
        """Assign permission to group"""
        # Check if group exists
        group = db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if permission exists
        permission = db.query(PermissionMaster).filter(PermissionMaster.permission_id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Check if already assigned
        existing = db.query(GroupPermissionMapping).filter(
            GroupPermissionMapping.group_id == group_id,
            GroupPermissionMapping.permission_id == permission_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already assigned to group"
            )
        
        try:
            mapping = GroupPermissionMapping(
                group_id=group_id,
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
                detail="Failed to assign permission to group"
            )
    
    @staticmethod
    def remove_permission_from_group(db: Session, group_id: UUID, permission_id: UUID) -> bool:
        """Remove permission from group"""
        mapping = db.query(GroupPermissionMapping).filter(
            GroupPermissionMapping.group_id == group_id,
            GroupPermissionMapping.permission_id == permission_id
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found in group"
            )
        
        db.delete(mapping)
        db.commit()
        return True
    
    @staticmethod
    def get_group_permissions(db: Session, group_id: UUID) -> List[PermissionMaster]:
        """Get all permissions assigned to a group"""
        mappings = db.query(GroupPermissionMapping).filter(GroupPermissionMapping.group_id == group_id).all()
        permission_ids = [m.permission_id for m in mappings]
        permissions = db.query(PermissionMaster).filter(PermissionMaster.permission_id.in_(permission_ids)).all()
        return permissions

