from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

# 1. Import Group models
from app.models.group import GroupMaster, GroupUserMapping

# 2. Import Role models (GroupRoleMapping is here now)
from app.models.role import RoleMaster, GroupRoleMapping

# 3. Import Permission models (GroupPermissionMapping is here now)
from app.models.permission import PermissionMaster, GroupPermissionMapping

from app.models.user import UserDetails
from app.models.tenant import TenantMaster
from app.schemas.group import GroupCreate, GroupUpdate

class GroupService:
    @staticmethod
    def create_group(db: Session, group_data: GroupCreate) -> GroupMaster:
        """Create a new group"""
        # Check if tenant exists AND is active
        tenant = db.query(TenantMaster).filter(
            TenantMaster.tenant_id == group_data.tenant_id,
            TenantMaster.is_active == True
        ).first()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found or inactive"
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
        """Get group by ID (Returns inactive groups too)"""
        return db.query(GroupMaster).filter(GroupMaster.group_id == group_id).first()
    
    @staticmethod
    def get_groups(db: Session, tenant_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[GroupMaster]:
        """Get list of ALL groups (Active and Inactive)"""
        query = db.query(GroupMaster)
        
        if tenant_id:
            query = query.filter(GroupMaster.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_group(db: Session, group_id: UUID, group_data: GroupUpdate) -> GroupMaster:
        """Update group"""
        # Allow updating inactive groups (e.g., to reactivate them)
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
        """Soft delete group"""
        db_group = db.query(GroupMaster).filter(
            GroupMaster.group_id == group_id,
            GroupMaster.is_active == True
        ).first()
        
        if not db_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        db_group.is_active = False
        db.commit()
        return True
    
    # ============ USER MAPPINGS ============
    @staticmethod
    def assign_user_to_group(db: Session, user_id: UUID, group_id: UUID) -> GroupUserMapping:
        """Assign user to group"""
        # Check if user exists AND is active
        user = db.query(UserDetails).filter(
            UserDetails.user_id == user_id,
            UserDetails.is_active == True
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive"
            )
        
        # Check if group exists AND is active
        group = db.query(GroupMaster).filter(
            GroupMaster.group_id == group_id,
            GroupMaster.is_active == True
        ).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found or inactive"
            )
        
        # Check if user and group belong to same tenant
        if user.tenant_id != group.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User and group must belong to the same tenant"
            )
        
        # Check if already assigned (Any state)
        existing = db.query(GroupUserMapping).filter(
            GroupUserMapping.user_id == user_id,
            GroupUserMapping.group_id == group_id
        ).first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already assigned to group"
                )
            else:
                # Reactivate assignment
                existing.is_active = True
                db.commit()
                db.refresh(existing)
                return existing
        
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
        """Soft remove user from group"""
        mapping = db.query(GroupUserMapping).filter(
            GroupUserMapping.user_id == user_id,
            GroupUserMapping.group_id == group_id,
            GroupUserMapping.is_active == True
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in group"
            )
        
        mapping.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_group_users(db: Session, group_id: UUID) -> List[UserDetails]:
        """Get all active users in a group"""
        return db.query(UserDetails).join(
            GroupUserMapping, GroupUserMapping.user_id == UserDetails.user_id
        ).filter(
            GroupUserMapping.group_id == group_id,
            GroupUserMapping.is_active == True,
            UserDetails.is_active == True
        ).all()
    
    @staticmethod
    def get_user_groups(db: Session, user_id: UUID) -> List[GroupMaster]:
        """Get all active groups a user belongs to"""
        return db.query(GroupMaster).join(
            GroupUserMapping, GroupUserMapping.group_id == GroupMaster.group_id
        ).filter(
            GroupUserMapping.user_id == user_id,
            GroupUserMapping.is_active == True,
            GroupMaster.is_active == True
        ).all()
    
    # ============ ROLE MAPPINGS ============
    @staticmethod
    def assign_role_to_group(db: Session, group_id: UUID, role_id: UUID) -> GroupRoleMapping:
        """Assign role to group"""
        # Check active group
        group = db.query(GroupMaster).filter(
            GroupMaster.group_id == group_id,
            GroupMaster.is_active == True
        ).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found or inactive"
            )
        
        # Check active role
        role = db.query(RoleMaster).filter(
            RoleMaster.role_id == role_id,
            RoleMaster.is_active == True
        ).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found or inactive"
            )
        
        if group.tenant_id != role.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group and role must belong to the same tenant"
            )
        
        existing = db.query(GroupRoleMapping).filter(
            GroupRoleMapping.group_id == group_id,
            GroupRoleMapping.role_id == role_id
        ).first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role already assigned to group"
                )
            else:
                # Reactivate assignment
                existing.is_active = True
                db.commit()
                db.refresh(existing)
                return existing
        
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
        """Soft remove role from group"""
        mapping = db.query(GroupRoleMapping).filter(
            GroupRoleMapping.group_id == group_id,
            GroupRoleMapping.role_id == role_id,
            GroupRoleMapping.is_active == True
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found in group"
            )
        
        mapping.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_group_roles(db: Session, group_id: UUID) -> List[RoleMaster]:
        """Get all active roles assigned to a group"""
        return db.query(RoleMaster).join(
            GroupRoleMapping, GroupRoleMapping.role_id == RoleMaster.role_id
        ).filter(
            GroupRoleMapping.group_id == group_id,
            GroupRoleMapping.is_active == True,
            RoleMaster.is_active == True
        ).all()
    
    # ============ PERMISSION MAPPINGS ============
    @staticmethod
    def assign_permission_to_group(db: Session, group_id: UUID, permission_id: UUID) -> GroupPermissionMapping:
        """Assign permission to group"""
        # Check active group
        group = db.query(GroupMaster).filter(
            GroupMaster.group_id == group_id,
            GroupMaster.is_active == True
        ).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found or inactive"
            )
        
        # Check active permission
        permission = db.query(PermissionMaster).filter(
            PermissionMaster.permission_id == permission_id,
            PermissionMaster.is_active == True
        ).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found or inactive"
            )
        
        existing = db.query(GroupPermissionMapping).filter(
            GroupPermissionMapping.group_id == group_id,
            GroupPermissionMapping.permission_id == permission_id
        ).first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Permission already assigned to group"
                )
            else:
                # Reactivate assignment
                existing.is_active = True
                db.commit()
                db.refresh(existing)
                return existing
        
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
        """Soft remove permission from group"""
        mapping = db.query(GroupPermissionMapping).filter(
            GroupPermissionMapping.group_id == group_id,
            GroupPermissionMapping.permission_id == permission_id,
            GroupPermissionMapping.is_active == True
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found in group"
            )
        
        mapping.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_group_permissions(db: Session, group_id: UUID) -> List[PermissionMaster]:
        """Get all active permissions assigned to a group"""
        return db.query(PermissionMaster).join(
            GroupPermissionMapping, GroupPermissionMapping.permission_id == PermissionMaster.permission_id
        ).filter(
            GroupPermissionMapping.group_id == group_id,
            GroupPermissionMapping.is_active == True,
            PermissionMaster.is_active == True
        ).all()