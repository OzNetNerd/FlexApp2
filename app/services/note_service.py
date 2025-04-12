# note_service.py

import logging
from typing import Dict, Any, List, Optional
from app.models import Note
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)


class NoteService(CRUDService):
    """Custom service for Note model with polymorphic relationship support."""

    def __init__(self):
        """Initialize with Note model."""
        super().__init__(Note)

    def validate_create(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate input data for creating a new note.

        Args:
            data (Dict[str, Any]): Input data.

        Returns:
            List[str]: List of validation errors (empty if valid).
        """
        errors = []
        required_fields = ["content", "notable_type", "notable_id", "user_id"]

        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} is required.")

        return errors

    def validate_update(self, entity: Note, data: Dict[str, Any]) -> List[str]:
        """
        Validate input data for updating an existing note.

        Args:
            entity (Note): Existing note instance.
            data (Dict[str, Any]): Updated data.

        Returns:
            List[str]: List of validation errors (empty if valid).
        """
        errors = []

        # No specific update validations for now
        return errors

    def get_by_notable(self, notable_type: str, notable_id: int) -> List[Note]:
        """
        Get all notes for a specific entity.

        Args:
            notable_type (str): Type of entity (Company, Contact, etc.)
            notable_id (int): ID of the entity

        Returns:
            List[Note]: List of Notes
        """
        try:
            return Note.query.filter_by(
                notable_type=notable_type,
                notable_id=notable_id
            ).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error getting notes for {notable_type} {notable_id}: {e}")
            raise