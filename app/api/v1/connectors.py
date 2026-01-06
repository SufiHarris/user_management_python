from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.connector import ConnectorCreate, ConnectorUpdate, ConnectorResponse
from app.schemas.common import ResponseBase
from app.services.connector_service import ConnectorService

router = APIRouter()

@router.post("/", response_model=ConnectorResponse, status_code=status.HTTP_201_CREATED)
def create_connector(
    connector_data: ConnectorCreate,
    db: Session = Depends(get_db)
):
    """Create a new connector"""
    connector = ConnectorService.create_connector(db, connector_data)
    return connector

@router.get("/{connector_id}", response_model=ConnectorResponse)
def get_connector(
    connector_id: UUID,
    db: Session = Depends(get_db)
):
    """Get connector by ID"""
    connector = ConnectorService.get_connector_by_id(db, connector_id)
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    return connector

@router.get("/", response_model=List[ConnectorResponse])
def list_connectors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all connectors"""
    connectors = ConnectorService.get_connectors(db, skip=skip, limit=limit)
    return connectors

@router.post("/{connector_id}/update", response_model=ConnectorResponse)
def update_connector(
    connector_id: UUID,
    connector_data: ConnectorUpdate,
    db: Session = Depends(get_db)
):
    """Update connector"""
    connector = ConnectorService.update_connector(db, connector_id, connector_data)
    return connector

@router.post("/{connector_id}/delete", response_model=ResponseBase)
def delete_connector(
    connector_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete connector"""
    ConnectorService.delete_connector(db, connector_id)
    return ResponseBase(success=True, message="Connector deleted successfully")
