import json
import logging
import traceback
from typing import Dict, Tuple, List
from flask import request, jsonify

logger = logging.getLogger(__name__)


class DataRouteHandler:
    """Handles data-related routes for grid components with pagination, sorting, and filtering."""

    def __init__(self, service, model, json_validator):
        """
        Initialize the DataRouteHandler.

        Args:
            service: Service instance to interact with the database layer.
            model: SQLAlchemy model class.
            json_validator: Utility to ensure JSON-serializability.
        """
        self.service = service
        self.model = model
        self.json_validator = json_validator

    def parse_request_params(self) -> Tuple[int, int, int, str, str, Dict]:
        """
        Parse pagination, sorting, and filtering parameters from the request.

        Returns:
            Tuple containing:
            - page (int): current page number
            - page_size (int): number of items per page
            - start_row (int): index of first item
            - sort_column (str): field to sort by
            - sort_direction (str): 'asc' or 'desc'
            - filter_model (dict): filtering parameters
        """
        start_row = request.args.get("startRow", 0, type=int)
        end_row = request.args.get("endRow", 15, type=int)
        page_size = end_row - start_row
        page = (start_row // page_size) + 1 if page_size > 0 else 1

        logger.debug(f"Pagination: page={page}, page_size={page_size}")

        sort_model = request.args.get("sortModel", "[]")
        try:
            sort_model = json.loads(sort_model)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"❌  Error parsing sortModel JSON: {e}")
            sort_model = []

        filter_model = request.args.get("filterModel", "{}")
        try:
            filter_model = json.loads(filter_model)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"❌  Error parsing filterModel JSON: {e}")
            filter_model = {}

        sort_column = sort_model[0].get("colId", "id") if sort_model else "id"
        sort_direction = sort_model[0].get("sort", "asc") if sort_model else "asc"

        return page, page_size, start_row, sort_column, sort_direction, filter_model

    def format_data_items(self, items) -> List[Dict]:
        """
        Convert model objects to dictionaries and validate for JSON output.

        Args:
            items: List of SQLAlchemy model instances.

        Returns:
            List[Dict]: List of cleaned dictionaries.
        """
        data = []
        for item in items:
            item_dict = item.to_dict() if hasattr(item, "to_dict") else {k: v for k, v in item.__dict__.items() if not k.startswith("_")}
            data.append(self.json_validator.ensure_json_serializable(item_dict))
        return data

    def handle_data_request(self):
        """
        Main handler for the data route.

        Returns:
            Flask JSON response with paginated and filtered results.

        Raises:
            500 response with error traceback on failure.
        """
        try:
            page, page_size, start_row, sort_column, sort_direction, filter_model = self.parse_request_params()

            items = self.service.get_all(
                page=page,
                per_page=page_size,
                sort_column=sort_column,
                sort_direction=sort_direction,
                filters=filter_model,
            )

            logger.debug(f"Found {len(items.items)} items out of {items.total} total")

            data = self.format_data_items(items.items)

            return jsonify(
                {
                    "data": data,
                    "total": items.total if hasattr(items, "total") else len(data),
                    "page": page,
                    "per_page": page_size,
                }
            )

        except Exception as e:
            logger.error(f"❌  Error in data route: {str(e)}")
            logger.error(f"❌  Traceback: {traceback.format_exc()}")
            return (
                jsonify({"error": str(e), "data": [], "total": 0, "page": 1, "per_page": 15}),
                500,
            )
