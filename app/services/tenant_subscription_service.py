from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.tenant_subscription import TenantSubscription
from app.models.tenant import TenantMaster
from app.models.module import ModuleMaster
from app.schemas.tenant_subscription import TenantSubscriptionCreate, TenantSubscriptionUpdate

class TenantSubscriptionService:
    @staticmethod
    def create_subscription(db: Session, subscription_data: TenantSubscriptionCreate, created_by: Optional[UUID] = None) -> TenantSubscription:
        """Create a new tenant subscription"""
        # Check if tenant exists
        tenant = db.query(TenantMaster).filter(TenantMaster.tenant_id == subscription_data.tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Check if module exists
        module = db.query(ModuleMaster).filter(ModuleMaster.module_id == subscription_data.module_id).first()
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Check if subscription already exists
        existing = db.query(TenantSubscription).filter(
            TenantSubscription.tenant_id == subscription_data.tenant_id,
            TenantSubscription.module_id == subscription_data.module_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription already exists for this tenant and module"
            )
        
        try:
            db_subscription = TenantSubscription(
                tenant_id=subscription_data.tenant_id,
                module_id=subscription_data.module_id,
                subscription_start_date=subscription_data.subscription_start_date,
                subscription_end_date=subscription_data.subscription_end_date,
                created_by=created_by
            )
            
            db.add(db_subscription)
            db.commit()
            db.refresh(db_subscription)
            
            return db_subscription
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription creation failed"
            )
    
    @staticmethod
    def get_subscription_by_id(db: Session, subscription_id: UUID) -> Optional[TenantSubscription]:
        """Get subscription by ID"""
        return db.query(TenantSubscription).filter(TenantSubscription.subscription_id == subscription_id).first()
    
    @staticmethod
    def get_subscriptions(db: Session, tenant_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[TenantSubscription]:
        """Get list of subscriptions"""
        query = db.query(TenantSubscription)
        
        if tenant_id:
            query = query.filter(TenantSubscription.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_subscription(db: Session, subscription_id: UUID, subscription_data: TenantSubscriptionUpdate, updated_by: Optional[UUID] = None) -> TenantSubscription:
        """Update subscription"""
        db_subscription = db.query(TenantSubscription).filter(TenantSubscription.subscription_id == subscription_id).first()
        
        if not db_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        update_data = subscription_data.model_dump(exclude_unset=True)
        update_data['updated_by'] = updated_by
        
        for field, value in update_data.items():
            setattr(db_subscription, field, value)
        
        try:
            db.commit()
            db.refresh(db_subscription)
            return db_subscription
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed"
            )
    
    @staticmethod
    def delete_subscription(db: Session, subscription_id: UUID) -> bool:
        """Delete subscription"""
        db_subscription = db.query(TenantSubscription).filter(TenantSubscription.subscription_id == subscription_id).first()
        
        if not db_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        db.delete(db_subscription)
        db.commit()
        return True
    
    @staticmethod
    def get_tenant_modules(db: Session, tenant_id: UUID) -> List[ModuleMaster]:
        """Get all modules subscribed by a tenant"""
        subscriptions = db.query(TenantSubscription).filter(
            TenantSubscription.tenant_id == tenant_id,
            TenantSubscription.is_active == True
        ).all()
        
        module_ids = [sub.module_id for sub in subscriptions]
        modules = db.query(ModuleMaster).filter(ModuleMaster.module_id.in_(module_ids)).all()
        
        return modules