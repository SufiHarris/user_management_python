from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class ConnectorBase(BaseModel):
    database_name: str = Field(..., min_length=1, max_length=255)
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(default=5432)
    username: str = Field(..., min_length=1, max_length=255)
    config_method: Optional[str] = Field(None, max_length=100)
    cache_memory: Optional[int] = None

class ConnectorCreate(ConnectorBase):
    password: str = Field(..., min_length=1)

class ConnectorUpdate(BaseModel):
    database_name: Optional[str] = Field(None, min_length=1, max_length=255)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = None
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = None
    config_method: Optional[str] = Field(None, max_length=100)
    cache_memory: Optional[int] = None
    is_active: Optional[bool] = None

class ConnectorResponse(ConnectorBase):
    connector_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)