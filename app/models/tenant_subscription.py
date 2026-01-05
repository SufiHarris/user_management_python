from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class TenantSubscription(Base):
    __tablename__ = "tenant_subscription"
    
    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenant_master.tenant_id", ondelete="CASCADE"), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey("module_master.module_id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    subscription_start_date = Column(Date, nullable=True)
    subscription_end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    tenant = relationship("TenantMaster", back_populates="subscriptions")
    module = relationship("ModuleMaster", back_populates="tenant_subscriptions")