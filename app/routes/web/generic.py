from dataclasses import dataclass, field
from typing import Optional, List, Type, Any, Dict
from flask import request, redirect, url_for, flash, Blueprint, Request
from flask_login import login_required
import logging
from datetime import datetime

from app.services.crud_service import CRUDService
from app.routes.base.crud_base import CRUDRoutesBase
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.json_validator import JSONValidator
from app.routes.base.components.request_logger import RequestLogger
from app.services.table_config_manager import TableConfigManager
from app.services.data_route_handler import DataRouteHandler
from app.routes.base.components.entity_handler import EntityHandler, ResourceContext, TableContext
from app.services.item_manager import ItemManager
from app.services.relationship_service import RelationshipService
from app.routes.base.components.autocomplete import get_autocomplete_field

logger = logging.getLogger(__name__)
GENERIC_TEMPLATE = "entity_table.html"


@dataclass
class GenericWebRoutes(CRUDRoutesBase):
    """
    Generic web routes for CRUD operations.

    This class sets up standard CRUD (Create, Read, Update, Delete) routes for a given model
    within a specified Flask blueprint. It also manages related services such as JSON validation,
    request logging, table configuration, and data handling.
    """

    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    index_template: str = GENERIC_TEMPLATE
    view_template: Optional[str] = "create_view_edit/view.html"
    # view_template: Optional[str] = "tshoot.html"
    create_template: Optional[str] = "create_view_edit/create.html"
    edit_template: Optional[str] = "create_view_edit/edit.html"
    api_url_prefix: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Post-initialization to set up route dependencies and register endpoints.

        Initializes various services such as the CRUD service, JSON validator, request logger,
        table configuration manager, data handler, and item manager. Then, it creates the entity
        handler and registers all web routes.
        """
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
            EntityHandler: Configured handler with custom create and edit validation functions.
        """
        entity_handler = EntityHandler(self.model, self.service, self.json_validator)
        entity_handler.validate_create = self._validate_create_from_request
        entity_handler.validate_edit = self._validate_edit_from_request
        return entity_handler

    def _validate_create_from_request(self, request_obj: Request) -> List[str]:
        """
        Validate form data from the request object for creating a new item.

        Args:
            request_obj (Request): The incoming Flask request containing form data.

        Returns:
            List[str]: A list of error messages, if any.
        """
        return self._validate_create(request_obj.form.to_dict())

    def _validate_edit_from_request(self, item: Any, request_obj: Request) -> List[str]:
        """
        Validate form data from the request object for editing an existing item.

        Args:
            item (Any): The model instance to be edited.
            request_obj (Request): The incoming Flask request containing form data.

        Returns:
            List[str]: A list of error messages, if any.
        """
        return self._validate_edit(item, request_obj.form.to_dict())

    def _preprocess_form_data(self, request: Request) -> Dict[str, Any]:
        """
        Process and transform form data from the request.

        Converts form data to a dictionary, casts date strings to datetime objects,
        and processes multi-select fields (for 'users' and 'companies') by filtering out empty strings.

        Args:
            request (Request): The incoming Flask request object.

        Returns:
            Dict[str, Any]: The processed form data.
        """
        # Log the raw form data (with all values as lists)
        raw_data: Dict[str, List[str]] = request.form.to_dict(flat=False)
        logger.info(f"Raw form data (flat=False): {raw_data}")

        # Start with the basic form data (first value only for each field)
        form_data: Dict[str, Any] = request.form.to_dict()

        # Process multi-select fields
        if "users" in request.form:
            users_list: List[str] = request.form.getlist("users")
            form_data["users"] = [u for u in users_list if u]
        if "companies" in request.form:
            companies_list: List[str] = request.form.getlist("companies")
            form_data["companies"] = [c for c in companies_list if c]

        # Convert 'created_at' to datetime if present
        if "created_at" in form_data and form_data["created_at"]:
            try:
                form_data["created_at"] = datetime.fromisoformat(form_data["created_at"])
            except ValueError:
                logger.error("Invalid format for created_at. Expected ISO format.")

        # Convert 'updated_at' to datetime if present
        if "updated_at" in form_data and form_data["updated_at"]:
            try:
                form_data["updated_at"] = datetime.fromisoformat(form_data["updated_at"])
            except ValueError:
                logger.error("Invalid format for updated_at. Expected ISO format.")

        return form_data

    def _create_route(self) -> Any:
        """
        Handle requests for creating a new item.

        For POST requests, process the form submission; for GET requests, render the create form.

        Returns:
            Any: The response from handling the create operation.
        """
        self.request_logger.log_request_info(self.model.__name__, "create")
        if request.method == "POST":
            return self._handle_create_form_submission()
        return self._render_create_form()

    def _render_create_form(self) -> Any:
        """
        Render the form template for creating a new item.

        Prepares the context (including tabs and title) and safely renders the create form template.

        Returns:
            Any: The rendered create form.
        """
        item_dict: Dict[str, Any] = {}

        context = ResourceContext(
            model=self.model,
            blueprint_name=self.blueprint.name,
            item_dict=item_dict,

            title=f"Create a {self.model.__name__}",
            read_only=False
        )
        return render_safely(self.create_template, context, f"Error rendering create form for {self.model.__name__}")

    def _render_edit_form(self, item: Any) -> Any:
        """
        Render the form template for editing an existing item.

        Converts the item to a dictionary, prepares context with tabs, and safely renders the edit form.

        Args:
            item (Any): The model instance to be edited.

        Returns:
            Any: The rendered edit form.
        """
        item_dict: Dict[str, Any] = item.to_dict()

        context = ResourceContext(
            model=self.model,
            blueprint_name=self.blueprint.name,
            item_dict=item_dict,
            item=None,  # Placeholder for additional item data if needed
            title=f"Edit",
            read_only=False
        )

        return render_safely(self.edit_template, context, f"Error rendering edit form for {self.model.__name__}")

    def _delete_route(self, item_id: int) -> Any:
        """
        Handle the deletion of an item by its ID.

        Logs the deletion request, attempts to delete the item, flashes appropriate messages,
        and redirects to the index page.

        Args:
            item_id (int): The ID of the item to delete.

        Returns:
            Any: The redirect response to the index page.
        """
        self.request_logger.log_request_info(self.model.__name__, "delete", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, "error")
        else:
            success, error = self.item_manager.delete_item(item)
            if error:
                flash(error, "error")
            else:
                flash(f"{self.model.__name__} deleted successfully", "success")
        return redirect(url_for(f"{self.blueprint.name}.index"))

    def _data_route(self) -> Any:
        """
        Handle API requests for table data.

        Logs the request and delegates handling to the data route handler.

        Returns:
            Any: The data response for the table.
        """
        self.request_logger.log_request_info(self.model.__name__, "data")
        return self.data_handler.handle_data_request()

    def _handle_edit_form_submission(self, item: Any) -> Any:
        """
        Process the submitted form data for editing an existing item.

        Validates the form data, processes the submitted information, updates the item,
        logs the update, and flashes a success message upon completion.

        Args:
            item (Any): The model instance being edited.

        Returns:
            Any: The updated item or a rendered edit form with error messages.
        """
        errors = self.entity_handler.validate_edit(item, request)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_edit_form(item)

        logger.info(f"Raw form data received for edit (item ID {item.id}): {request.form.to_dict(flat=False)}")
        form_data = self._preprocess_form_data(request)
        logger.info(f"Processed submitted data for edit (item ID {item.id}): {form_data}")

        result, error = self.item_manager.update_item(item, form_data)
        if error:
            flash(error, "error")
            return self._render_edit_form(item)

        if hasattr(result, "to_dict"):
            logger.info(f"Database entry updated: {result.to_dict()}")
        else:
            logger.info(f"Database entry updated: {result}")
        flash(f"{self.model.__name__} updated successfully", "success")
        return result

    def _edit_route(self, item_id: int) -> Any:
        """
        Handle requests for editing an existing item by its ID.

        Logs the edit request, retrieves the item, validates the form if it's a POST request,
        and either processes the edit or renders the edit form.

        Args:
            item_id (int): The ID of the item to edit.

        Returns:
            Any: The response from handling the edit operation.
        """
        self.request_logger.log_request_info(self.model.__name__, "edit", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error or item is None:
            flash("Item not found.", "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))
        if request.method == "POST":
            return self._handle_edit_form_submission(item)
        return self._render_edit_form(item)

    def _index_route(self) -> Any:
        """
        Render the index page displaying a table of items.

        Retrieves table configuration and constructs the context for the index template,
        which is then safely rendered.

        Returns:
            Any: The rendered index page.
        """
        self.request_logger.log_request_info(self.model.__name__, "index")
        table_config = self.table_config_manager.get_table_config(self.model.__tablename__)
        data_url = self._determine_data_url()
        context = TableContext(
            page_type="index",
            title=f"{self.model.__name__}s",
            table_config=table_config,
            table_id=f"{self.model.__tablename__}_table",
            data_url=data_url,
            entity_name=self.model.__name__,
            add_url=url_for(f"{self.blueprint.name}.create"),
            columns=table_config.get("columns", []),
        )
        return render_safely(self.index_template, context, f"Error rendering {self.model.__name__} index")

    def _handle_create_form_submission(self) -> Any:
        """
        Process the submitted form data for creating a new item.

        Validates the form data, processes the submitted information, creates the item,
        logs the creation, and flashes a success message upon completion.

        Returns:
            Any: The created item or a rendered create form with error messages.
        """
        errors = self.entity_handler.validate_create(request)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_create_form()

        logger.info(f"Raw form data received for create: {request.form.to_dict(flat=False)}")
        form_data = self._preprocess_form_data(request)
        logger.info(f"Processed submitted data for create: {form_data}")

        result, error = self.item_manager.create_item(form_data)
        if error:
            flash(error, "error")
            return self._render_create_form()

        if hasattr(result, "to_dict"):
            logger.info(f"Database entry created: {result.to_dict()}")
        else:
            logger.info(f"Database entry created: {result}")
        flash(f"{self.model.__name__} created successfully", "success")
        return result

    def _register_routes(self) -> None:
        """
        Register all necessary web routes with the Flask blueprint.

        Routes include endpoints for index, view, create, edit, delete, and data table API requests.
        """
        self.blueprint.add_url_rule("/", "index", login_required(self._index_route), methods=["GET"])
        self.blueprint.add_url_rule("/<int:item_id>", "view", login_required(self._view_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/create", "create", login_required(self._create_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/edit", "edit", login_required(self._edit_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/delete", "delete", login_required(self._delete_route), methods=["POST"])
        self.blueprint.add_url_rule("/data", "data", login_required(self._data_route), methods=["GET"])

    def _determine_data_url(self) -> str:
        """
        Construct the URL for table data API requests.

        Returns:
            str: The URL for accessing table data, either using the provided API URL prefix
                 or the blueprint's 'data' endpoint.
        """
        return f"{self.api_url_prefix}/{self.model.__tablename__}" if self.api_url_prefix else url_for(
            f"{self.blueprint.name}.data"
        )

    @staticmethod
    def _get_item_display_name(item: Any) -> str:
        """
        Retrieve a user-friendly display name for a given item.

        Checks common attributes ('name', 'title', 'email', or 'username'). If the item
        has both 'first_name' and 'last_name', it concatenates them; otherwise, it falls back
        to the item's ID.

        Args:
            item (Any): The item instance.

        Returns:
            str: A user-friendly display name for the item.
        """
        for attr in ["name", "title", "email", "username"]:
            if hasattr(item, attr) and getattr(item, attr):
                return getattr(item, attr)
        if hasattr(item, "first_name") and hasattr(item, "last_name"):
            return f"{item.first_name} {item.last_name}".strip()
        return str(item.id)

    def _view_route(self, item_id: int) -> Any:
        """
        Handle requests to view an item by its ID.

        Logs the request, retrieves the item, processes relationships (if the model is 'User'),
        prepares the context with tabs, and safely renders the view template.

        Args:
            item_id (int): The ID of the item to view.

        Returns:
            Any: The rendered view template or a redirect if errors occur.
        """
        self.request_logger.log_request_info(self.model.__name__, "view", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)

        if error:
            flash(error, "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))

        if request.method == "POST":
            return self._handle_view_post(item)

        item_dict: Dict[str, Any] = item.to_dict()

        if self.model.__name__ == "User":
            # Retrieve relationships for a User model
            relationships = RelationshipService.get_relationships_for_entity('user', item_id)
            item_dict['related_users'] = [rel for rel in relationships if rel['entity_type'] == 'user']
            item_dict['related_companies'] = [rel for rel in relationships if rel['entity_type'] == 'company']

        logger.info(f"This is item: {item_dict}")

        # tabs = self.create_tabs_function()
        #
        # # Update 'Mappings' tab entries with relationship data for User models
        # if self.model.__name__ == "User":
        #     for tab in tabs:
        #         if tab.tab_name == "Mappings":
        #             for section in tab.sections:
        #                 for entry in section.entries:
        #                     if entry.entry_name == "users" and 'related_users' in item_dict:
        #                         entry.value = item_dict['related_users']
        #                     elif entry.entry_name == "companies" and 'related_companies' in item_dict:
        #                         entry.value = item_dict['related_companies']


        context = ResourceContext(
            model=self.model,
            blueprint_name=self.blueprint.name,
            item_dict=item_dict,
            item=None,  # Placeholder for additional item data if needed
            title="Viewing",
            read_only=True
        )

        return render_safely(self.view_template, context,
                             f"Error viewing {self.model.__name__} with id {item_id}")

    def add_context(self, item: Any, context: Dict[str, Any], edit_mode: bool) -> None:
        """
        Add additional context to the template rendering context, including relationships and autocomplete fields.

        For User models, adds autocomplete fields based on related relationships.

        Args:
            item (Any): The item instance for which context is being added.
            context (Dict[str, Any]): The current context dictionary to update.
            edit_mode (bool): Flag indicating whether the context is for edit mode.
        """
        logger.debug(f"Adding relationships to the context for {self.model.__name__} {item.id}.")
        relationships = RelationshipService.get_relationships_for_entity('user', item.id)
        logger.info(f"Retrieved {len(relationships)} relationships for user with ID {item.id}.")
        logger.debug(f"Payload: {relationships}")

        # Optionally add relationships to context:
        # context["relationships"] = relationships

        if self.model.__name__ == "User":
            context["autocomplete_fields"] = [
                get_autocomplete_field("Users", relationships=relationships),
                get_autocomplete_field("Companies", relationships=relationships)
            ]

        logger.debug(f"Added {len(context.get('autocomplete_fields', []))} autocomplete fields to the {edit_mode} context.")
