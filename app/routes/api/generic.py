from dataclasses import dataclass, field
from typing import List, Type
from flask import request, jsonify, Blueprint
import logging
import traceback
from app.routes.base.crud_base import CRUDRoutesBase, CRUDService

logger = logging.getLogger(__name__)


@dataclass
class GenericAPIRoutes(CRUDRoutesBase):
    """
    Generic REST API class that provides CRUD endpoints for any SQLAlchemy model.

    Attributes:
        blueprint (Blueprint): The Flask blueprint to register routes with.
        model (Type): SQLAlchemy model associated with the routes.
        api_prefix (str): Optional API prefix for routing.
        service (CRUDService): CRUD service for business logic.
        required_fields (List[str]): Fields required for create/update validation.
        unique_fields (List[str]): Fields that must be unique.
    """

    blueprint: Blueprint
    model: Type
    api_prefix: str = ""
    service: CRUDService = field(default_factory=CRUDService)
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initializes the service and registers routes after dataclass instantiation."""
        super().__post_init__()
        self.service = CRUDService(model_class=self.model)
        self._register_routes()
        logger.info(f"API routes registered for {self.model.__name__}.")

    def _register_routes(self):
        """Registers the standard list, get, create, update, and delete routes."""
        logger.info(f"Registering API routes for {self.model.__name__}.")
        self.blueprint.add_url_rule("/", "list", self._list_route, methods=["GET"])
        self.blueprint.add_url_rule("/<int:entity_id>", "get", self._get_route, methods=["GET"])
        self.blueprint.add_url_rule("/", "create", self._create_route, methods=["POST"])
        self.blueprint.add_url_rule("/<int:entity_id>", "update", self._update_route, methods=["PUT", "PATCH"])
        self.blueprint.add_url_rule("/<int:entity_id>", "delete", self._delete_route, methods=["DELETE"])

    def _list_route(self):
        """
        Handle GET request to list all entities with pagination, sorting, and filtering.

        Returns:
            Response: A JSON response containing a list of entities and pagination metadata.
        """
        logger.info(f"Handling API list route for {self.model.__name__}")
        try:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 25, type=int)
            sort_column = request.args.get("sort_by", "id")
            sort_direction = request.args.get("order", "asc")
            filters = {k.split(".")[1]: {"type": "contains", "filter": v} for k, v in request.args.items() if k.startswith("filter.")}

            entities = self.service.get_all(
                page=page,
                per_page=per_page,
                sort_column=sort_column,
                sort_direction=sort_direction,
                filters=filters,
            )

            data = [self._ensure_json_serializable(entity.to_dict()) for entity in entities.entities]
            return (
                jsonify(
                    {
                        "data": data,
                        "meta": {
                            "page": page,
                            "per_page": per_page,
                            "total": entities.total,
                            "pages": entties.pages,
                        },
                    }
                ),
                200,
            )
        except Exception as e:
            logger.error(f"❌  Error in list route: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

    def _get_route(self, entity_id: int):
        """
        Handle GET request for a single entity by ID.

        Args:
            entity_id (int): The ID of the entity.

        Returns:
            Response: A JSON response containing the entity or error message.
        """
        logger.info(f"Handling API get route for {self.model.__name__} with ID {entity_id}")
        try:
            entity = self.service.get_by_id(self.model, entity_id)
            return jsonify({"data": self._ensure_json_serializable(entity.to_dict())}), 200
        except Exception as e:
            logger.error(f"❌  Error in get route: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify(
                {
                    "error": "Not Found" if "404" in str(e) else "Internal Server Error",
                    "message": str(e),
                }
            ), (404 if "404" in str(e) else 500)

    def _create_route(self):
        """
        Handle POST request to create a new entity.

        Returns:
            Response: A JSON response containing the entity or validation errors.
        """
        logger.info(f"Handling API create route for {self.model.__name__}")
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            errors = self._validate_create(data)
            if errors:
                return jsonify({"error": "Validation Error", "messages": errors}), 400

            item = self.service.create(self.model, data)
            return (
                jsonify(
                    {
                        "data": self._ensure_json_serializable(entity.to_dict()),
                        "message": f"{self.model.__name__} created successfully",
                    }
                ),
                201,
            )
        except Exception as e:
            logger.error(f"❌  Error in create route: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

    def _update_route(self, entity_id: int):
        """
        Handle PUT/PATCH request to update an entity.

        Args:
            entity_id (int): The ID of the entity to update.

        Returns:
            Response: A JSON response with the updated entity or validation errors.
        """
        logger.info(f"Handling API update route for {self.model.__name__} with ID {entity_id}")
        try:
            item = self.service.get_by_id(self.model, entity_id)
            data = request.get_json() if request.is_json else request.form.to_dict()
            errors = self._validate_edit(item, data)
            if errors:
                return jsonify({"error": "Validation Error", "messages": errors}), 400

            item = self.service.update(item, data)
            return (
                jsonify(
                    {
                        "data": self._ensure_json_serializable(item.to_dict()),
                        "message": f"{self.model.__name__} updated successfully",
                    }
                ),
                200,
            )
        except Exception as e:
            logger.error(f"❌  Error in update route: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

    def _delete_route(self, entity_id: int):
        """
        Handle DELETE request to remove an item.

        Args:
            entity_id (int): The ID of the item to delete.

        Returns:
            Response: A confirmation JSON message.
        """
        logger.info(f"Handling API delete route for {self.model.__name__} with ID {entity_id}")
        try:
            item = self.service.get_by_id(self.model, entity_id)
            self.service.delete(item)
            return jsonify({"message": f"{self.model.__name__} deleted successfully"}), 200
        except Exception as e:
            logger.error(f"❌  Error in delete route: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
