from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

# Base Response Models
class ResponseBase(BaseModel):
    success: bool = True
    message: str
    
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    details: Optional[str] = None

# Pagination
class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)

class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: list

# Base timestamp mixin
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)