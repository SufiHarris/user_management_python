from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class ConnectorMaster(Base):
    __tablename__ = "connector_master"
    
    connector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=5432)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # Should be encrypted in production
    config_method = Column(String(100), nullable=True)  # e.g., 'direct', 'ssh_tunnel', 'ssl'
    cache_memory = Column(Integer, nullable=True)  # Cache size in MB
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), nullable=True)
