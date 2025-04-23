# services/note_service.py

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models import Note
from app.services.crud_service import CRUDService

from app.utils.app_logging import get_logger

logger = get_logger()


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
            return Note.query.filter_by(notable_type=notable_type, notable_id=notable_id).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error getting notes for {notable_type} {notable_id}: {e}")
            raise

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Note]:
        """
        Get notes created within a date range.

        Args:
            start_date (str): Start date in format YYYY-MM-DD
            end_date (str): End date in format YYYY-MM-DD

        Returns:
            List[Note]: List of notes within the date range
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            # Add a day to end_date to make it inclusive
            end = end + timedelta(days=1)

            return Note.query.filter(Note.created_at >= start, Note.created_at < end).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error getting notes by date range: {e}")
            raise

    def get_by_days_ago(self, days_ago: int) -> List[Note]:
        """
        Get notes created within the last X days.

        Args:
            days_ago (int): Number of days to look back

        Returns:
            List[Note]: List of notes created within the specified days
        """
        try:
            start_date = datetime.now() - timedelta(days=int(days_ago))

            return Note.query.filter(Note.created_at >= start_date).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error getting notes by days ago: {e}")
            raise

    def search_by_content(self, search_term: str) -> List[Note]:
        """
        Search notes by content.

        Args:
            search_term (str): Term to search for in note content

        Returns:
            List[Note]: List of notes matching the search term
        """
        try:
            search_pattern = f"%{search_term}%"
            return (
                Note.query.filter(or_(Note.content.ilike(search_pattern), Note.processed_content.ilike(search_pattern)))
                .order_by(Note.created_at.desc())
                .all()
            )
        except Exception as e:
            logger.error(f"❌ Error searching notes: {e}")
            raise

    def get_by_user_id(self, user_id: int) -> List[Note]:
        """
        Get notes created by a specific user.

        Args:
            user_id (int): ID of the user

        Returns:
            List[Note]: List of notes by the user
        """
        try:
            return Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error getting notes by user ID {user_id}: {e}")
            raise
