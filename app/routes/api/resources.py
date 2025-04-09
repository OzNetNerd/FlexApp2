# api/resources.py

import logging
import traceback
from flask import Blueprint, request, jsonify
from sqlalchemy import inspect, desc
from werkzeug.exceptions import BadRequest
from typing import Type, Dict, Any, Callable, List, Optional, Union

logger = logging.getLogger(__name__)


class GenericDataAPI:
    """
    Factory class for creating generic data API endpoints for different resource types.
    """

    def __init__(self, app=None):
        """
        Initialize the GenericDataAPI with an optional Flask app.

        Args:
            app: Flask application instance to register blueprints with
        """
        self.resources = {}
        self.resource_models = {}
        self.resource_blueprints = {}
        self.custom_query_handlers = {}
        self.custom_formatters = {}

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Register all blueprints with the Flask app.

        Args:
            app: Flask application instance
        """
        for resource_type, blueprint in self.resource_blueprints.items():
            logger.info(f"Registering API blueprint for resource: {resource_type}")
            app.register_blueprint(blueprint)

    def register_resource(
        self,
        resource_type: str,
        model: Type[Any],
        search_fields: List[str] = None,
        default_sort: str = "id",
        query_handler: Callable = None,
        formatter: Callable = None,
        url_prefix: str = "/api",
    ):
        """
        Register a resource type with the API.

        Args:
            resource_type: The resource type identifier (e.g., 'users', 'companies')
            model: The SQLAlchemy model class for this resource
            search_fields: List of model fields to search when filtering
            default_sort: Default field to sort by
            query_handler: Optional custom query handler function
            formatter: Optional custom formatter function for response data
            url_prefix: URL prefix for the blueprint
        """
        if resource_type in self.resources:
            logger.warning(f"Resource type {resource_type} already registered, overwriting.")

        logger.info(f"🔧 Registering resource type: {resource_type}")
        logger.debug(f"📝 Model: {model.__name__}")
        logger.debug(f"📝 Search fields: {search_fields or ['name']}")
        logger.debug(f"📝 Default sort: {default_sort}")
        logger.debug(f"📝 Custom query handler: {query_handler.__name__ if query_handler else None}")
        logger.debug(f"📝 Custom formatter: {formatter.__name__ if formatter else None}")

        self.resources[resource_type] = {"model": model, "search_fields": search_fields or ["name"], "default_sort": default_sort}

        self.resource_models[resource_type] = model

        if query_handler:
            self.custom_query_handlers[resource_type] = query_handler

        if formatter:
            self.custom_formatters[resource_type] = formatter

        # Create a blueprint for this resource
        bp_name = f"{resource_type}_api"
        blueprint = Blueprint(bp_name, __name__, url_prefix=f"{url_prefix}/{resource_type}")

        # Register the data endpoint on the blueprint
        @blueprint.route("/data", methods=["GET"])
        def get_data():
            logger.info(f"🔍 API data request for resource: {resource_type}")
            logger.debug(f"📝 Request ID: {id(request)}")
            logger.debug(f"📝 Request method: {request.method}")
            logger.debug(f"📝 Request path: {request.path}")
            logger.debug(f"📝 Request args: {request.args}")
            logger.debug(f"📝 Request headers: {dict(request.headers)}")
            return self._handle_data_request(resource_type)

        self.resource_blueprints[resource_type] = blueprint
        logger.info(f"Registered resource type {resource_type} with blueprint {bp_name}")

        return blueprint

    def _handle_data_request(self, resource_type: str):
        """
        Handle a data request for the specified resource type.

        Args:
            resource_type: The resource type identifier

        Returns:
            Flask response with JSON data
        """
        request_start_log = f"Processing API data request for {resource_type}"
        logger.info(request_start_log)

        try:
            # Get resource configuration
            resource_config = self.resources.get(resource_type)
            if not resource_config:
                logger.warning(f"❌ Resource type {resource_type} not found")
                return jsonify({"error": f"Resource type {resource_type} not found"}), 404

            model = resource_config["model"]
            search_fields = resource_config["search_fields"]
            default_sort = resource_config["default_sort"]

            # Parse query parameters
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)
            search = request.args.get("search", "")
            sort_by = request.args.get("sort", default_sort)
            order = request.args.get("order", "asc")

            logger.debug(f"📝 Request parameters - page: {page}, per_page: {per_page}")
            logger.debug(f"📝 Search term: '{search}'")
            logger.debug(f"📝 Sort by: {sort_by}, Order: {order}")

            # Validate sort field exists on model
            model_columns = [column.key for column in inspect(model).columns]
            if sort_by not in model_columns and sort_by != default_sort:
                logger.warning(f"⚠️ Invalid sort field: {sort_by}, defaulting to {default_sort}")
                sort_by = default_sort

            # Check if there's a custom query handler for this resource
            if resource_type in self.custom_query_handlers:
                logger.debug(f"🔧 Using custom query handler for {resource_type}")
                query = self.custom_query_handlers[resource_type](
                    model=model, search=search, sort_by=sort_by, order=order, **request.args.to_dict()
                )
            else:
                # Start with base query
                logger.debug(f"🔧 Building standard query for {resource_type}")
                query = model.query

                # Apply search if provided
                if search and search_fields:
                    logger.debug(f"🔍 Applying search filter: '{search}' on fields {search_fields}")
                    search_filters = []
                    for field in search_fields:
                        if hasattr(model, field):
                            column = getattr(model, field)
                            search_filters.append(column.ilike(f"%{search}%"))

                    if search_filters:
                        from sqlalchemy import or_

                        query = query.filter(or_(*search_filters))

                # Apply sorting
                if hasattr(model, sort_by):
                    logger.debug(f"Applying sort: {sort_by} {order}")
                    if order.lower() == "desc":
                        query = query.order_by(desc(getattr(model, sort_by)))
                    else:
                        query = query.order_by(getattr(model, sort_by))

            # Apply pagination
            logger.debug(f"📄 Applying pagination: page {page}, per_page {per_page}")
            paginated = query.paginate(page=page, per_page=per_page)
            logger.debug(f"📊 Query returned {paginated.total} total records across {paginated.pages} pages")

            # Format items
            if resource_type in self.custom_formatters:
                logger.debug(f"🔧 Using custom formatter for {resource_type}")
                formatted_items = self.custom_formatters[resource_type](paginated.items)
            else:
                # Default formatting - try to_dict() or fallback to dynamic attribute mapping
                logger.debug(f"🔧 Using default formatter for {resource_type}")
                formatted_items = []
                for item in paginated.items:
                    if hasattr(item, "to_dict"):
                        formatted_items.append(item.to_dict())
                    else:
                        entity_dict = {}
                        for column in model_columns:
                            entity_dict[column] = getattr(item, column, None)
                        formatted_items.append(entity_dict)

            # Prepare response
            response = {"data": formatted_items, "total": paginated.total, "page": page, "per_page": per_page, "pages": paginated.pages}

            logger.info(f"Successfully processed API data request for {resource_type}")
            logger.debug(f"📝 Response contains {len(formatted_items)} items")
            logger.debug(f"📝 Response JSON size: {len(str(response))} chars")

            return jsonify(response)

        except Exception as e:
            logger.exception(f"❌ Error handling data request for {resource_type}: {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return jsonify({"error": str(e), "type": type(e).__name__}), 500
