from dataclasses import dataclass, field
from typing import Optional, List, Type, Any

from flask import Blueprint, Request
from flask_login import login_required

import logging

from app.services.crud_service import CRUDService
from app.routes.base.crud_base import CRUDRoutesBase
from app.routes.base.components.json_validator import JSONValidator
from app.routes.base.components.request_logger import RequestLogger
from app.services.table_config_manager import TableConfigManager
from app.services.data_route_handler import DataRouteHandler
from app.services.item_manager import ItemManager
from app.routes.base.components.entity_handler import EntityHandler

from app.routes.web.generic_crud.create import create_route
from app.routes.web.generic_crud.edit import edit_route
from app.routes.web.generic_crud.view import view_route
from app.routes.web.generic_crud.delete import delete_route
from app.routes.web.generic_crud.data import data_route
from app.routes.web.generic_crud.index import index_route

logger = logging.getLogger(__name__)
GENERIC_TEMPLATE = "entity_table.html"


@dataclass
class GenericWebRoutes(CRUDRoutesBase):
    """
    Generic web routes for CRUD operations.
    """

    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    index_template: str = GENERIC_TEMPLATE
    view_template: Optional[str] = "pages/crud/view.html"
    create_template: Optional[str] = "pages/crud/create.html"
    edit_template: Optional[str] = "pages/crud/edit.html"
    api_url_prefix: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.service: CRUDService = CRUDService(self.model)
        self.json_validator: JSONValidator = JSONValidator()
        self.request_logger: RequestLogger = RequestLogger()
        self.table_config_manager: TableConfigManager = TableConfigManager(self.json_validator)
        self.data_handler: DataRouteHandler = DataRouteHandler(self.service, self.model, self.json_validator)
        self.item_manager: ItemManager = ItemManager(self.model, self.service, self.blueprint.name)
        self.entity_handler: EntityHandler = self._create_entity_handler()
        self._register_routes()
        logger.debug(f"Web CRUD routes registered for {self.model.__name__} model.")

    def _create_entity_handler(self) -> EntityHandler:
        """
        Create and configure the entity handler for form validation.

        Returns:
            EntityHandler: Configured handler with custom create/edit validation methods.
        """
        entity_handler = EntityHandler(self.model, self.service, self.json_validator)
        entity_handler.validate_create = self._validate_create_from_request
        entity_handler.validate_edit = self._validate_edit_from_request
        return entity_handler

    def _validate_create_from_request(self, request_obj: Request) -> List[str]:
        """
        Validate form data from the request object for creating a new item.

        Args:
            request_obj (Request): The incoming Flask request.

        Returns:
            List[str]: A list of validation error messages.
        """
        return self._validate_create(request_obj.form.to_dict())

    def _validate_edit_from_request(self, item: Any, request_obj: Request) -> List[str]:
        """
        Validate form data from the request object for editing an existing item.

        Args:
            item (Any): The model instance being edited.
            request_obj (Request): The incoming Flask request.

        Returns:
            List[str]: A list of validation error messages.
        """
        return self._validate_edit(item, request_obj.form.to_dict())

    def _register_routes(self) -> None:
        """
        Register all CRUD and data routes on the blueprint.
        """
        self.blueprint.add_url_rule("/", "index", login_required(index_route.__get__(self)), methods=["GET"])
        self.blueprint.add_url_rule("/<int:item_id>", "view", login_required(view_route.__get__(self)), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/create", "create", login_required(create_route.__get__(self)), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/edit", "edit", login_required(edit_route.__get__(self)), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/delete", "delete", login_required(delete_route.__get__(self)), methods=["POST"])
        self.blueprint.add_url_rule("/data", "data", login_required(data_route.__get__(self)), methods=["GET"])
