from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class PermissionMaster(Base):
    __tablename__ = "permission_master"
    
    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_name = Column(String(100), nullable=False, unique=True)
    resource = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_resource_action'),
    )
    
    # Relationships
    user_mappings = relationship("PermissionUserMapping", back_populates="permission", cascade="all, delete-orphan")
    role_mappings = relationship("RolePermissionMapping", back_populates="permission", cascade="all, delete-orphan")
    group_mappings = relationship("GroupPermissionMapping", back_populates="permission", cascade="all, delete-orphan")

class PermissionUserMapping(Base):
    __tablename__ = "permission_user_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission_master.permission_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.user_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("user_details.user_id"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('permission_id', 'user_id', name='uq_permission_user'),
    )
    
    # Relationships - FIX: Specify foreign_keys to avoid ambiguity
    permission = relationship("PermissionMaster", back_populates="user_mappings")
    user = relationship("UserDetails", foreign_keys=[user_id], back_populates="user_permissions")
    assigner = relationship("UserDetails", foreign_keys=[assigned_by])

class GroupPermissionMapping(Base):
    __tablename__ = "group_permission_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group_master.group_id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission_master.permission_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('group_id', 'permission_id', name='uq_group_permission'),
    )
    
    # Relationships
    group = relationship("GroupMaster", back_populates="group_permissions")
    permission = relationship("PermissionMaster", back_populates="group_mappings")