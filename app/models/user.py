from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class UserDetails(Base):
    __tablename__ = "user_details"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenant_master.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships - FIX: Specify foreign_keys to avoid ambiguity
    tenant = relationship("TenantMaster", back_populates="users")
    user_roles = relationship(
        "UserRoleMapping", 
        foreign_keys="UserRoleMapping.user_id",
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    user_permissions = relationship(
        "PermissionUserMapping",
        foreign_keys="PermissionUserMapping.user_id",
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    user_groups = relationship("GroupUserMapping", back_populates="user", cascade="all, delete-orphan")