# app/services/note/core.py
from datetime import datetime
from typing import List, Optional

from app.models import Note
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin
from app.utils.app_logging import get_logger

logger = get_logger()


class NoteCoreService(CRUDService, ValidatorMixin):
    """Core service for Note CRUD operations."""

    def __init__(self):
        """Initialize the Note core service."""
        super().__init__(model_class=Note)

    def get_by_notable(self, notable_type: str, notable_id: int) -> List[Note]:
        """Fetch notes for a given entity, newest first."""
        try:
            return (
                self.model_class.query.filter_by(notable_type=notable_type, notable_id=notable_id)
                .order_by(self.model_class.created_at.desc())
                .all()
            )
        except Exception as e:
            logger.error(f"❌ Error getting notes for {notable_type} id={notable_id}: {e}")
            raise

    def get_by_notable_with_filters(
        self, notable_type: str, notable_id: int, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> List[Note]:
        """
        Get notes for a specific notable entity with optional date range filtering.
        Date parameters should be ISO format strings.
        """
        try:
            query = self.model_class.query.filter_by(notable_type=notable_type, notable_id=notable_id)

            if from_date and to_date:
                logger.info(f"Applying date filter: from={from_date}, to={to_date}")
                # Parse ISO format strings with timezone consideration
                start = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
                end = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
                query = query.filter(self.model_class.created_at.between(start, end))

            return query.order_by(self.model_class.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ Error querying notes for {notable_type} id={notable_id} with date filter: {e}")
            raise

    def validate_create(self, data: dict) -> list[str]:
        """Validate note creation data."""
        errors = []
        required_fields = ["content", "notable_type", "notable_id", "user_id"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors
