# app/services/note_service.py

from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_

from app.models import Note
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()


class NoteService(CRUDService):
    """Service for Note model with polymorphic relationship and search helpers."""

    def __init__(self):
        """
        Initialize with Note model, enforcing the core fields on create.
        """
        super().__init__(Note, required_fields=["content", "notable_type", "notable_id", "user_id"])

    def get_by_notable(self, notable_type: str, notable_id: int) -> List[Note]:
        """Fetch notes for a given entity, newest first."""
        try:
            return Note.query.filter_by(notable_type=notable_type, notable_id=notable_id).order_by(
                Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error getting notes for {notable_type} id={notable_id}: {e}")
            raise

    def get_by_notable_with_filters(self, notable_type: str, notable_id: int,
                                    from_date: Optional[str] = None,
                                    to_date: Optional[str] = None) -> List[Note]:
        """
        Get notes for a specific notable entity with optional date range filtering.
        Date parameters should be ISO format strings.
        """
        try:
            query = Note.query.filter_by(notable_type=notable_type, notable_id=notable_id)

            if from_date and to_date:
                logger.info(f"Applying date filter: from={from_date}, to={to_date}")
                # Parse ISO format strings with timezone consideration
                start = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                end = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                query = query.filter(Note.created_at.between(start, end))

            return query.order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error querying notes for {notable_type} id={notable_id} with date filter: {e}")
            raise

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Note]:
        """
        Get notes within a date range using ISO format dates.
        Handles timezone-aware ISO strings properly.
        """
        try:
            # Parse ISO format strings directly
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

            logger.info(f"Querying notes between {start} and {end}")
            return Note.query.filter(Note.created_at.between(start, end)).all()
        except Exception as e:
            logger.error(f"❌ Error querying notes between {start_date} and {end_date}: {e}")
            raise

    def search(self, term: str) -> List[Note]:
        """
        Simple text search over note content.
        """
        try:
            pattern = f"%{term}%"
            return Note.query.filter(or_(Note.content.ilike(pattern), Note.user_id == term)).order_by(
                Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error searching notes for '{term}': {e}")
            raise