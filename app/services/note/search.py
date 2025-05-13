# app/services/note/search.py
from datetime import datetime
from typing import List
from sqlalchemy import or_

from app.models import Note
from app.services.service_base import ServiceBase
from app.utils.app_logging import get_logger

logger = get_logger()


class NoteSearchService(ServiceBase):
    """Service for Note search operations."""

    def __init__(self):
        """Initialize the Note search service."""
        super().__init__()

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Note]:
        """
        Get notes within a date range using ISO format dates.
        Handles timezone-aware ISO strings properly.
        """
        try:
            # Parse ISO format strings directly
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

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
            return Note.query.filter(or_(Note.content.ilike(pattern), Note.user_id == term)).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error searching notes for '{term}': {e}")
            raise
