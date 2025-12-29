from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class RoleMaster(Base):
    __tablename__ = "role_master"
    
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenant_master.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    role_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'role_name', name='uq_tenant_role_name'),
    )
    
    # Relationships
    tenant = relationship("TenantMaster", back_populates="roles")
    user_mappings = relationship("UserRoleMapping", back_populates="role", cascade="all, delete-orphan")
    permission_mappings = relationship("RolePermissionMapping", back_populates="role", cascade="all, delete-orphan")
    group_mappings = relationship("GroupRoleMapping", back_populates="role", cascade="all, delete-orphan")

class UserRoleMapping(Base):
    __tablename__ = "user_role_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.user_id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role_master.role_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("user_details.user_id"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    
    # Relationships - FIX: Specify foreign_keys to avoid ambiguity
    user = relationship("UserDetails", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("RoleMaster", back_populates="user_mappings")
    assigner = relationship("UserDetails", foreign_keys=[assigned_by])

class RolePermissionMapping(Base):
    __tablename__ = "role_permission_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role_master.role_id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission_master.permission_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    
    # Relationships
    role = relationship("RoleMaster", back_populates="permission_mappings")
    permission = relationship("PermissionMaster", back_populates="role_mappings")

class GroupRoleMapping(Base):
    __tablename__ = "group_role_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group_master.group_id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role_master.role_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('group_id', 'role_id', name='uq_group_role'),
    )
    
    # Relationships
    group = relationship("GroupMaster", back_populates="group_roles")
    role = relationship("RoleMaster", back_populates="group_mappings")