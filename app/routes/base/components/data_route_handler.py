import json
import logging
import traceback
from typing import Dict, Tuple, List
from flask import request, jsonify

logger = logging.getLogger(__name__)


class DataRouteHandler:
    """Handles data route functionality for grid data."""

    def __init__(self, service, model, json_validator):
        self.service = service
        self.model = model
        self.json_validator = json_validator

    def parse_request_params(self) -> Tuple[int, int, int, str, str, Dict]:
        """Parse and validate data request parameters."""
        # Parse pagination parameters
        start_row = request.args.get('startRow', 0, type=int)
        end_row = request.args.get('endRow', 15, type=int)
        page_size = end_row - start_row
        page = (start_row // page_size) + 1 if page_size > 0 else 1
        logger.debug(f"Pagination: page={page}, page_size={page_size}")

        # Parse sorting parameters
        sort_model = request.args.get('sortModel', '[]')
        try:
            sort_model = json.loads(sort_model)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing sortModel JSON: {e}")
            sort_model = []

        # Parse filtering parameters
        filter_model = request.args.get('filterModel', '{}')
        try:
            filter_model = json.loads(filter_model)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing filterModel JSON: {e}")
            filter_model = {}

        # Get sort parameters
        sort_column = 'id'
        sort_direction = 'asc'
        if sort_model and len(sort_model) > 0:
            sort_column = sort_model[0].get('colId', 'id')
            sort_direction = sort_model[0].get('sort', 'asc')

        return page, page_size, start_row, sort_column, sort_direction, filter_model

    def format_data_items(self, items) -> List[Dict]:
        """Convert model objects to JSON-serializable dictionaries."""
        data = []
        for item in items:
            if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                item_dict = item.to_dict()
            else:
                item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
            data.append(self.json_validator.ensure_json_serializable(item_dict))
        return data

    def handle_data_request(self):
        """Process data request and return JSON response."""
        try:
            # Parse request parameters
            page, page_size, start_row, sort_column, sort_direction, filter_model = self.parse_request_params()

            # Get data using service layer
            items = self.service.get_all(
                self.model,
                page=page,
                per_page=page_size,
                sort_column=sort_column,
                sort_direction=sort_direction,
                filters=filter_model
            )

            logger.debug(f"Found {len(items.items)} items out of {items.total} total")

            # Format data for response
            data = self.format_data_items(items.items)

            # Prepare response
            result = {
                'data': data,
                'total': items.total if hasattr(items, 'total') else len(data),
                'page': page,
                'per_page': page_size
            }

            logger.debug(f"Returning {len(data)} items in the data route.")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in data route: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': str(e),
                'data': [],
                'total': 0,
                'page': 1,
                'per_page': 15
            }), 500