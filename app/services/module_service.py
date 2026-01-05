from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.module import ModuleMaster
from app.schemas.module import ModuleCreate, ModuleUpdate

class ModuleService:
    @staticmethod
    def create_module(db: Session, module_data: ModuleCreate, created_by: Optional[UUID] = None) -> ModuleMaster:
        """Create a new module"""
        try:
            db_module = ModuleMaster(
                module_name=module_data.module_name,
                description=module_data.description,
                created_by=created_by
            )
            
            db.add(db_module)
            db.commit()
            db.refresh(db_module)
            
            return db_module
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Module with this name already exists"
            )
    
    @staticmethod
    def get_module_by_id(db: Session, module_id: UUID) -> Optional[ModuleMaster]:
        """Get module by ID"""
        return db.query(ModuleMaster).filter(ModuleMaster.module_id == module_id).first()
    
    @staticmethod
    def get_modules(db: Session, skip: int = 0, limit: int = 100) -> List[ModuleMaster]:
        """Get list of modules"""
        return db.query(ModuleMaster).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_module(db: Session, module_id: UUID, module_data: ModuleUpdate, updated_by: Optional[UUID] = None) -> ModuleMaster:
        """Update module"""
        db_module = db.query(ModuleMaster).filter(ModuleMaster.module_id == module_id).first()
        
        if not db_module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        update_data = module_data.model_dump(exclude_unset=True)
        update_data['updated_by'] = updated_by
        
        for field, value in update_data.items():
            setattr(db_module, field, value)
        
        try:
            db.commit()
            db.refresh(db_module)
            return db_module
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed"
            )
    
    @staticmethod
    def delete_module(db: Session, module_id: UUID) -> bool:
        """Delete module"""
        db_module = db.query(ModuleMaster).filter(ModuleMaster.module_id == module_id).first()
        
        if not db_module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db.delete(db_module)
        db.commit()
        return True