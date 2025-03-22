from dataclasses import dataclass, field
from typing import  List, Type
from flask import  request, jsonify, Blueprint
import logging
import traceback
from routes.base.crud_base import CRUDRoutesBase, CRUDService


logger = logging.getLogger(__name__)


@dataclass
class GenericAPIRoutes(CRUDRoutesBase):
    """
    Handles API routes for CRUD operations.
    Returns JSON responses for programmatic consumption.
    """

    blueprint: Blueprint
    model: Type
    api_prefix: str = ''
    service: CRUDService = field(default_factory=CRUDService)
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)

    def __post_init__(self):
        """
        Initialize and register API routes.
        """
        super().__post_init__()
        self._register_routes()
        logger.debug(f"API routes registered for {self.model.__name__} model.")

    def _register_routes(self):
        """
        Register standard API routes.
        """
        logger.debug(f"Registering API routes for {self.model.__name__}.")

        # List endpoint
        self.blueprint.add_url_rule(
            '/',
            'list',
            self._list_route,
            methods=['GET']
        )

        # Get single item endpoint
        self.blueprint.add_url_rule(
            '/<int:item_id>',
            'get',
            self._get_route,
            methods=['GET']
        )

        # Create endpoint
        self.blueprint.add_url_rule(
            '/',
            'create',
            self._create_route,
            methods=['POST']
        )

        # Update endpoint
        self.blueprint.add_url_rule(
            '/<int:item_id>',
            'update',
            self._update_route,
            methods=['PUT', 'PATCH']
        )

        # Delete endpoint
        self.blueprint.add_url_rule(
            '/<int:item_id>',
            'delete',
            self._delete_route,
            methods=['DELETE']
        )

    def _list_route(self):
        """
        Get list of items with pagination, sorting and filtering.
        """
        logger.debug(f"Handling API list route for {self.model.__name__}.")
        logger.debug(f"Request: {request.path} | Args: {dict(request.args)} | Headers: {dict(request.headers)}")

        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 25, type=int)

            # Get sorting parameters
            sort_column = request.args.get('sort_by', 'id')
            sort_direction = request.args.get('order', 'asc')

            # Get filter parameters
            filter_model = {}
            for key, value in request.args.items():
                if key.startswith('filter.'):
                    field = key.split('.')[1]
                    filter_model[field] = {
                        'type': 'contains',
                        'filter': value
                    }

            # Get items using service layer
            items = self.service.get_all(
                self.model,
                page=page,
                per_page=per_page,
                sort_column=sort_column,
                sort_direction=sort_direction,
                filters=filter_model
            )

            # Convert items to dictionaries
            data = []
            for item in items.items:
                if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                    item_dict = item.to_dict()
                else:
                    item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
                data.append(self._ensure_json_serializable(item_dict))

            result = {
                'data': data,
                'meta': {
                    'page': page,
                    'per_page': per_page,
                    'total': items.total,
                    'pages': items.pages
                }
            }

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in API list route: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(e)
            }), 500

    def _get_route(self, item_id):
        """
        Get a single item by ID.
        """
        logger.debug(f"Handling API get route for {self.model.__name__} with id {item_id}.")
        logger.debug(f"Request: {request.path} | Args: {dict(request.args)} | Headers: {dict(request.headers)}")

        try:
            item = self.service.get_by_id(self.model, item_id)

            # Convert item to dictionary
            if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                item_dict = item.to_dict()
            else:
                item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}

            item_dict = self._ensure_json_serializable(item_dict)

            result = {
                'data': item_dict
            }

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in API get route for item {item_id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Item Not Found' if '404' in str(e) else 'Internal Server Error',
                'message': str(e)
            }), 404 if '404' in str(e) else 500

    def _create_route(self):
        """
        Create a new item.
        """
        logger.debug(f"Handling API create route for {self.model.__name__}.")
        logger.debug(f"Request: {request.path} | Method: {request.method} | Headers: {dict(request.headers)}")

        try:
            # Get data from request
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            logger.debug(f"Received data with {len(data)} fields")

            # Validate data
            validation_errors = self._validate_create(data)
            if validation_errors:
                logger.debug(f"Validation errors: {validation_errors}")
                return jsonify({
                    'error': 'Validation Error',
                    'messages': validation_errors
                }), 400

            # Create item
            item = self.service.create(self.model, data)
            logger.info(f"{self.model.__name__} created successfully with id {item.id}")

            # Convert item to dictionary
            if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                item_dict = item.to_dict()
            else:
                item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}

            item_dict = self._ensure_json_serializable(item_dict)

            result = {
                'data': item_dict,
                'message': f'{self.model.__name__} created successfully'
            }

            return jsonify(result), 201

        except Exception as e:
            logger.error(f"Error in API create route: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(e)
            }), 500

    def _update_route(self, item_id):
        """
        Update an existing item.
        """
        logger.debug(f"Handling API update route for {self.model.__name__} with id {item_id}.")
        logger.debug(f"Request: {request.path} | Method: {request.method} | Headers: {dict(request.headers)}")

        try:
            # Get item
            item = self.service.get_by_id(self.model, item_id)

            # Get data from request
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            logger.debug(f"Received data with {len(data)} fields")

            # Validate data
            validation_errors = self._validate_edit(item, data)
            if validation_errors:
                logger.debug(f"Validation errors: {validation_errors}")
                return jsonify({
                    'error': 'Validation Error',
                    'messages': validation_errors
                }), 400

            # Update item
            item = self.service.update(item, data)
            logger.info(f"{self.model.__name__} with id {item_id} updated successfully")

            # Convert item to dictionary
            if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                item_dict = item.to_dict()
            else:
                item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}

            item_dict = self._ensure_json_serializable(item_dict)

            result = {
                'data': item_dict,
                'message': f'{self.model.__name__} updated successfully'
            }

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in API update route for item {item_id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Item Not Found' if '404' in str(e) else 'Internal Server Error',
                'message': str(e)
            }), 404 if '404' in str(e) else 500

    def _delete_route(self, item_id):
        """
        Delete an item.
        """
        logger.debug(f"Handling API delete route for {self.model.__name__} with id {item_id}.")
        logger.debug(f"Request: {request.path} | Method: {request.method} | Headers: {dict(request.headers)}")

        try:
            # Get item
            item = self.service.get_by_id(self.model, item_id)

            # Delete item
            self.service.delete(item)
            logger.info(f"{self.model.__name__} with id {item_id} deleted successfully")

            result = {
                'message': f'{self.model.__name__} deleted successfully'
            }

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in API delete route for item {item_id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Item Not Found' if '404' in str(e) else 'Internal Server Error',
                'message': str(e)
            }), 404 if '404' in str(e) else 500