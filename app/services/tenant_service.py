from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tenant import TenantMaster
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:

    @staticmethod
    def create_tenant(db: Session, tenant_data: TenantCreate) -> TenantMaster:
        """Create a new tenant"""
        try:
            db_tenant = TenantMaster(
                tenant_name=tenant_data.tenant_name
            )

            db.add(db_tenant)
            db.commit()
            db.refresh(db_tenant)

            return db_tenant

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this name already exists"
            )

    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: UUID) -> Optional[TenantMaster]:
        """Get tenant by ID"""
        return (
            db.query(TenantMaster)
            .filter(TenantMaster.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def get_tenants(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[TenantMaster]:
        """Get list of tenants"""
        return (
            db.query(TenantMaster)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_tenant(
        db: Session,
        tenant_id: UUID,
        tenant_data: TenantUpdate
    ) -> TenantMaster:
        """Update tenant"""
        db_tenant = (
            db.query(TenantMaster)
            .filter(TenantMaster.tenant_id == tenant_id)
            .first()
        )

        if not db_tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        update_data = tenant_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_tenant, field, value)

        try:
            db.commit()
            db.refresh(db_tenant)
            return db_tenant

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed due to database constraint"
            )

    @staticmethod
    def delete_tenant(db: Session, tenant_id: UUID) -> bool:
        """Soft delete tenant"""
        db_tenant = (
            db.query(TenantMaster)
            .filter(TenantMaster.tenant_id == tenant_id)
            .first()
        )

        if not db_tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        db_tenant.is_active = False
        db.commit()
        return True
