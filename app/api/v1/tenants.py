from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.schemas.common import ResponseBase
from app.services.tenant_service import TenantService

router = APIRouter()

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant"""
    tenant = TenantService.create_tenant(db, tenant_data)
    return tenant

@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get tenant by ID"""
    tenant = TenantService.get_tenant_by_id(db, tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant

@router.get("/", response_model=List[TenantResponse])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all tenants"""
    tenants = TenantService.get_tenants(db, skip=skip, limit=limit)
    return tenants

@router.post("/{tenant_id}/update", response_model=TenantResponse)
def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db)
):
    """Update tenant"""
    tenant = TenantService.update_tenant(db, tenant_id, tenant_data)
    return tenant

@router.post("/{tenant_id}/delete", response_model=ResponseBase)
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete tenant (soft delete)"""
    TenantService.delete_tenant(db, tenant_id)
    return ResponseBase(success=True, message="Tenant deleted successfully")
