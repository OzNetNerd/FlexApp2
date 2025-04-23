# app/services/search_service.py

import traceback
from typing import Any, Dict, List, Type

from sqlalchemy import or_

from app.utils.app_logging import get_logger

logger = get_logger()


class SearchService:
    """
    Generic search service that performs simple text and equality filtering
    on a given SQLAlchemy model.
    """

    def __init__(self, model_class: Type, search_fields: List[str]):
        """
        Args:
            model_class (Type): SQLAlchemy model to search.
            search_fields (List[str]): Columns to apply ilike(text) searches.
        """
        self.model_class = model_class
        self.search_fields = search_fields

    def search(self, term: str, filters: Dict[str, Any] = None) -> List[Any]:
        """
        Search the model.

        Args:
            term (str): Text to search via ilike on each search_field.
            filters (dict, optional): Exact-match filters {column: value}.

        Returns:
            List[Any]: Matched model instances.
        """
        try:
            query = self.model_class.query
            if term:
                pattern = f"%{term}%"
                clauses = [getattr(self.model_class, f).ilike(pattern) for f in self.search_fields if hasattr(self.model_class, f)]
                if clauses:
                    query = query.filter(or_(*clauses))

            if filters:
                for col, val in filters.items():
                    if hasattr(self.model_class, col) and val is not None:
                        query = query.filter(getattr(self.model_class, col) == val)

            return query.all()

        except Exception as e:
            logger.error(f"❌ Error searching {self.model_class.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise
