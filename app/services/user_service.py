from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import UserDetails
from app.models.tenant import TenantMaster
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.utils.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserDetails:
        """Create a new user"""
        # Check if tenant exists
        tenant = db.query(TenantMaster).filter(
            TenantMaster.tenant_id == user_data.tenant_id
        ).first()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        if not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant is not active"
            )
        
        # Check if email already exists for this tenant
        existing_user = db.query(UserDetails).filter(
            UserDetails.tenant_id == user_data.tenant_id,
            UserDetails.email == user_data.email
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered for this tenant"
            )
        
        try:
            # Create user
            db_user = UserDetails(
                tenant_id=user_data.tenant_id,
                firstname=user_data.firstname,
                lastname=user_data.lastname,
                email=user_data.email,
                phone_number=user_data.phone_number,
                address=user_data.address,
                password_hash=get_password_hash(user_data.password)
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return db_user
        
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed due to database constraint"
            )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserDetails]:
        """Get user by ID"""
        return db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str, tenant_id: Optional[UUID] = None) -> Optional[UserDetails]:
        """Get user by email"""
        query = db.query(UserDetails).filter(UserDetails.email == email)
        
        if tenant_id:
            query = query.filter(UserDetails.tenant_id == tenant_id)
        
        return query.first()
    
    @staticmethod
    def get_users(db: Session, tenant_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[UserDetails]:
        """Get list of users"""
        query = db.query(UserDetails)
        
        if tenant_id:
            query = query.filter(UserDetails.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> UserDetails:
        """Update user"""
        db_user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed due to database constraint"
            )
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Delete user"""
        db_user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[UserDetails]:
        """Authenticate user"""
        user = db.query(UserDetails).filter(UserDetails.email == email).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user