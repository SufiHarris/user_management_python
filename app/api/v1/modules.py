from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse
from app.schemas.common import ResponseBase
from app.services.module_service import ModuleService

router = APIRouter()

@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new module"""
    module = ModuleService.create_module(db, module_data)
    return module

@router.get("/{module_id}", response_model=ModuleResponse)
def get_module(
    module_id: UUID,
    db: Session = Depends(get_db)
):
    """Get module by ID"""
    module = ModuleService.get_module_by_id(db, module_id)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    return module

@router.get("/", response_model=List[ModuleResponse])
def list_modules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all modules"""
    modules = ModuleService.get_modules(db, skip=skip, limit=limit)
    return modules

@router.post("/{module_id}/update", response_model=ModuleResponse)
def update_module(
    module_id: UUID,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db)
):
    """Update module"""
    module = ModuleService.update_module(db, module_id, module_data)
    return module

@router.post("/{module_id}/delete", response_model=ResponseBase)
def delete_module(
    module_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete module"""
    ModuleService.delete_module(db, module_id)
    return ResponseBase(success=True, message="Module deleted successfully")