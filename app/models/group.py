from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class GroupMaster(Base):
    __tablename__ = "group_master"
    
    group_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenant_master.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    group_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'group_name', name='uq_tenant_group_name'),
    )
    
    # Relationships
    tenant = relationship("TenantMaster", back_populates="groups")
    group_users = relationship("GroupUserMapping", back_populates="group", cascade="all, delete-orphan")
    group_roles = relationship("GroupRoleMapping", back_populates="group", cascade="all, delete-orphan")
    group_permissions = relationship("GroupPermissionMapping", back_populates="group", cascade="all, delete-orphan")

class GroupUserMapping(Base):
    __tablename__ = "group_user_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group_master.group_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.user_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='uq_group_user'),
    )
    
    # Relationships
    group = relationship("GroupMaster", back_populates="group_users")
    user = relationship("UserDetails", back_populates="user_groups")