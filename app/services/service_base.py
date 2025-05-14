# app/services/service_base.py

from typing import Any, Dict, List, Optional, Type, Union

from flask_sqlalchemy import Pagination

from app.models.base import db
from app.utils.app_logging import get_logger

logger = get_logger()


class CRUDService:
    """Base service class for CRUD operations on a model."""
    
    def __init__(self, model_class: Type[db.Model], required_fields: Optional[List[str]] = None):
        """
        Initialize the CRUD service.
        
        Args:
            model_class: The SQLAlchemy model class
            required_fields: Optional list of field names that are required when creating entities
        """
        self.model_class = model_class
        self.required_fields = required_fields or []
        
    def get_all(self, page: int = 1, per_page: int = 15, 
                sort_column: str = "id", sort_direction: str = "asc",
                filters: Optional[Dict[str, Any]] = None) -> Union[List[db.Model], Pagination]:
        """
        Get all entities with pagination, sorting and filtering.
        
        Args:
            page: Page number (starting from 1)
            per_page: Number of items per page
            sort_column: Column name to sort by
            sort_direction: Sort direction ('asc' or 'desc')
            filters: Dictionary of filters to apply
            
        Returns:
            List of entities or a Pagination object
        """
        query = self.model_class.query
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)
        
        # Apply sorting
        if hasattr(self.model_class, sort_column):
            column = getattr(self.model_class, sort_column)
            if sort_direction.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        # Apply pagination
        return query.paginate(page=page, per_page=per_page)
    
    def get_by_id(self, entity_id: Union[int, str]) -> Optional[db.Model]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            The entity or None if not found
        """
        return self.model_class.query.get(entity_id)
    
    def create(self, data: Dict[str, Any]) -> db.Model:
        """
        Create a new entity.
        
        Args:
            data: Dictionary with entity attributes
            
        Returns:
            The created entity
        """
        # Check required fields
        for field in self.required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' is missing")
        
        entity = self.model_class(**data)
        db.session.add(entity)
        db.session.commit()
        return entity
    
    def update(self, entity: db.Model, data: Dict[str, Any]) -> db.Model:
        """
        Update an existing entity.
        
        Args:
            entity: The entity to update
            data: Dictionary with updated attributes
            
        Returns:
            The updated entity
        """
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        db.session.commit()
        return entity
    
    def delete(self, entity_id: Union[int, str]) -> None:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
        """
        entity = self.get_by_id(entity_id)
        if entity:
            db.session.delete(entity)
            db.session.commit()


def create_crud_service(model: Type[db.Model], required_fields: Optional[List[str]] = None) -> CRUDService:
    """
    Factory function to create a CRUDService instance for a model.

    Args:
        model: The SQLAlchemy model class
        required_fields: Optional list of field names that are required when creating entities

    Returns:
        An instance of CRUDService for the model
    """
    return CRUDService(model_class=model, required_fields=required_fields)