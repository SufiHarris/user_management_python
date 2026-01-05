from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.connector import ConnectorMaster
from app.schemas.connector import ConnectorCreate, ConnectorUpdate

class ConnectorService:
    @staticmethod
    def create_connector(db: Session, connector_data: ConnectorCreate, created_by: Optional[UUID] = None) -> ConnectorMaster:
        """Create a new connector"""
        try:
            db_connector = ConnectorMaster(
                database_name=connector_data.database_name,
                host=connector_data.host,
                port=connector_data.port,
                username=connector_data.username,
                password=connector_data.password,  # In production, encrypt this
                config_method=connector_data.config_method,
                cache_memory=connector_data.cache_memory,
                created_by=created_by
            )
            
            db.add(db_connector)
            db.commit()
            db.refresh(db_connector)
            
            return db_connector
        
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connector creation failed"
            )
    
    @staticmethod
    def get_connector_by_id(db: Session, connector_id: UUID) -> Optional[ConnectorMaster]:
        """Get connector by ID"""
        return db.query(ConnectorMaster).filter(ConnectorMaster.connector_id == connector_id).first()
    
    @staticmethod
    def get_connectors(db: Session, skip: int = 0, limit: int = 100) -> List[ConnectorMaster]:
        """Get list of connectors"""
        return db.query(ConnectorMaster).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_connector(db: Session, connector_id: UUID, connector_data: ConnectorUpdate, updated_by: Optional[UUID] = None) -> ConnectorMaster:
        """Update connector"""
        db_connector = db.query(ConnectorMaster).filter(ConnectorMaster.connector_id == connector_id).first()
        
        if not db_connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connector not found"
            )
        
        update_data = connector_data.model_dump(exclude_unset=True)
        update_data['updated_by'] = updated_by
        
        for field, value in update_data.items():
            setattr(db_connector, field, value)
        
        try:
            db.commit()
            db.refresh(db_connector)
            return db_connector
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed"
            )
    
    @staticmethod
    def delete_connector(db: Session, connector_id: UUID) -> bool:
        """Delete connector"""
        db_connector = db.query(ConnectorMaster).filter(ConnectorMaster.connector_id == connector_id).first()
        
        if not db_connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connector not found"
            )
        
        db.delete(db_connector)
        db.commit()
        return True
