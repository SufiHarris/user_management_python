from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.tenant_subscription import TenantSubscriptionCreate, TenantSubscriptionUpdate, TenantSubscriptionResponse
from app.schemas.module import ModuleResponse
from app.schemas.common import ResponseBase
from app.services.tenant_subscription_service import TenantSubscriptionService

router = APIRouter()

@router.post("/", response_model=TenantSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription_data: TenantSubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant subscription"""
    subscription = TenantSubscriptionService.create_subscription(db, subscription_data)
    return subscription

@router.get("/{subscription_id}", response_model=TenantSubscriptionResponse)
def get_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db)
):
    """Get subscription by ID"""
    subscription = TenantSubscriptionService.get_subscription_by_id(db, subscription_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return subscription

@router.get("/", response_model=List[TenantSubscriptionResponse])
def list_subscriptions(
    tenant_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all subscriptions"""
    subscriptions = TenantSubscriptionService.get_subscriptions(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return subscriptions

@router.put("/{subscription_id}", response_model=TenantSubscriptionResponse)
def update_subscription(
    subscription_id: UUID,
    subscription_data: TenantSubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """Update subscription"""
    subscription = TenantSubscriptionService.update_subscription(db, subscription_id, subscription_data)
    return subscription

@router.delete("/{subscription_id}", response_model=ResponseBase)
def delete_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete subscription"""
    TenantSubscriptionService.delete_subscription(db, subscription_id)
    return ResponseBase(success=True, message="Subscription deleted successfully")

@router.get("/tenant/{tenant_id}/modules", response_model=List[ModuleResponse])
def get_tenant_modules(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all modules subscribed by a tenant"""
    modules = TenantSubscriptionService.get_tenant_modules(db, tenant_id)
    return modules
