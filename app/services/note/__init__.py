# app/services/note/__init__.py
from typing import List, Optional

from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.note.core import NoteCoreService
from app.services.note.search import NoteSearchService


class NoteService(ServiceBase):
    """Main service for managing notes."""

    def __init__(self):
        """Initialize the Note service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(NoteCoreService)
        self.search_service = ServiceRegistry.get(NoteSearchService)

    # Core CRUD operations - delegate to core service
    def get_by_id(self, note_id):
        """Get a note by ID."""
        return self.core.get_by_id(note_id)

    def get_all(self, page=1, per_page=15, sort_column="id", sort_direction="asc", filters=None):
        """Get all notes with pagination."""
        return self.core.get_all(page, per_page, sort_column, sort_direction, filters)

    def create(self, data):
        """Create a new note."""
        return self.core.create(data)

    def update(self, note_id_or_obj, data):
        """Update a note."""
        return self.core.update(note_id_or_obj, data)

    def delete(self, note_id):
        """Delete a note."""
        return self.core.delete(note_id)

    def get_by_notable(self, notable_type: str, notable_id: int) -> List:
        """Get notes for a notable entity."""
        return self.core.get_by_notable(notable_type, notable_id)

    def get_by_notable_with_filters(
        self, notable_type: str, notable_id: int, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> List:
        """Get filtered notes for a notable entity."""
        return self.core.get_by_notable_with_filters(notable_type, notable_id, from_date, to_date)

    # Search operations - delegate to search service
    def get_by_date_range(self, start_date: str, end_date: str) -> List:
        """Get notes within a date range."""
        return self.search_service.get_by_date_range(start_date, end_date)

    def search(self, term: str) -> List:
        """Search notes by term."""
        return self.search_service.search(term)