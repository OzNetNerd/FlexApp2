from dataclasses import dataclass, field
from typing import Optional, List, Type
from flask import request, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
import logging
from datetime import datetime

from app.services.crud_service import CRUDService
from app.routes.base.crud_base import CRUDRoutesBase
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.json_validator import JSONValidator
from app.routes.base.components.request_logger import RequestLogger
from app.routes.base.components.table_config_manager import TableConfigManager
from app.routes.base.components.data_route_handler import DataRouteHandler
from app.routes.base.components.form_handler import FormHandler, ResourceContext, TableContext
from app.routes.base.components.item_manager import ItemManager
from app.models import Company, CRISPScore, Note

logger = logging.getLogger(__name__)
GENERIC_TEMPLATE = "entity_table.html"


@dataclass
class GenericWebRoutes(CRUDRoutesBase):
    """Generic web routes for CRUD operations."""

    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    index_template: str = GENERIC_TEMPLATE
    view_template: Optional[str] = "create_view_edit/view.html"
    create_template: Optional[str] = "create_view_edit/create.html"
    edit_template: Optional[str] = "create_view_edit/edit.html"
    api_url_prefix: Optional[str] = None
    get_tabs_function: Optional[callable] = None

    def __post_init__(self):
        """Initializes route dependencies and registers endpoints."""
        super().__post_init__()
        self.service = CRUDService(self.model)
        self.json_validator = JSONValidator()
        self.request_logger = RequestLogger()
        self.table_config_manager = TableConfigManager(self.json_validator)
        self.data_handler = DataRouteHandler(self.service, self.model, self.json_validator)
        self.item_manager = ItemManager(self.model, self.service, self.blueprint.name)
        self.form_handler = self._create_form_handler()
        self._register_routes()
        logger.debug(f"Web CRUD routes registered for {self.model.__name__} model.")

    def _create_form_handler(self) -> FormHandler:
        """Creates and configures the form handler."""
        form_handler = FormHandler(self.model, self.service, self.json_validator)
        form_handler.validate_create = self._validate_create_from_request
        form_handler.validate_edit = self._validate_edit_from_request
        return form_handler

    def _register_routes(self):
        """Registers all necessary web routes with the blueprint."""
        self.blueprint.add_url_rule("/", "index", login_required(self._index_route), methods=["GET"])
        self.blueprint.add_url_rule("/<int:item_id>", "view", login_required(self._view_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/create", "create", login_required(self._create_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/edit", "edit", login_required(self._edit_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/delete", "delete", login_required(self._delete_route), methods=["POST"])
        self.blueprint.add_url_rule("/data", "data", login_required(self._data_route), methods=["GET"])

    def _determine_data_url(self) -> str:
        """Constructs the data URL used for table API requests."""
        return f"{self.api_url_prefix}/{self.model.__tablename__}" if self.api_url_prefix else url_for(f"{self.blueprint.name}.data")

    def _index_route(self):
        """Serves the index (table list) page."""
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

    @staticmethod
    def _get_item_display_name(item) -> str:
        """Returns a user-friendly name for the given item."""
        for attr in ["name", "title", "email", "username"]:
            if hasattr(item, attr) and getattr(item, attr):
                return getattr(item, attr)
        if hasattr(item, "first_name") and hasattr(item, "last_name"):
            return f"{item.first_name} {item.last_name}".strip()
        return str(item.id)

    def _view_route(self, item_id: int):
        """Handles requests to view an item by ID.

        Args:
            item_id (int): The ID of the item.
        Returns:
            Response: Rendered view template.
        """
        self.request_logger.log_request_info(self.model.__name__, "view", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)

        if error:
            flash(error, "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))

        if request.method == "POST":
            return self._handle_view_post(item)

        # Get the basic item data
        item_dict = item.to_dict()

        # For User models, fetch relationships directly
        if self.model.__name__ == "User":
            from app.services.relationship_service import RelationshipService

            # Get all relationships from the service
            relationships = RelationshipService.get_relationships_for_entity('user', item_id)

            # Add relationship data to the item dictionary
            item_dict['related_users'] = [rel for rel in relationships if rel['entity_type'] == 'user']
            item_dict['related_companies'] = [rel for rel in relationships if rel['entity_type'] == 'company']

        logger.info(f"This is item: {item_dict}")

        # Get tabs configuration
        tabs = self.get_tabs_function(item_dict)

        # Update the 'users' and 'companies' tab entries with actual relationship data
        if self.model.__name__ == "User":
            for tab in tabs:
                if tab.tab_name == "Mappings":
                    for section in tab.sections:
                        for entry in section.entries:
                            if entry.entry_name == "users" and 'related_users' in item_dict:
                                entry.value = item_dict['related_users']
                            elif entry.entry_name == "companies" and 'related_companies' in item_dict:
                                entry.value = item_dict['related_companies']

        # Create the context for the template
        resource_context = ResourceContext.create_context(
            model=self.model,
            blueprint_name=self.blueprint.name,
            item_dict=item_dict,
            tabs=tabs,
            title="Viewing",
            read_only=True
        )

        return render_safely(self.view_template, resource_context,
                             f"Error viewing {self.model.__name__} with id {item_id}")

    def _handle_view_post(self, item):
        """Handles POST action for the view page, usually note submission."""
        note_content = request.form.get("note")
        if not note_content:
            flash("Note content is required.", "error")
            return redirect(url_for(f"{self.blueprint.name}.view", item_id=item.id))
        note = Note(content=note_content, user_id=current_user.id, parent_type=self.model.__name__, parent_id=item.id)
        try:
            note.save()
            flash("Note added successfully", "success")
        except Exception as e:
            logger.exception(f"Error saving note: {e}")
            flash("Failed to save note", "error")
        return redirect(url_for(f"{self.blueprint.name}.view", item_id=item.id))

    def _create_route(self):
        """Handles requests to create a new item."""
        self.request_logger.log_request_info(self.model.__name__, "create")
        if request.method == "POST":
            return self._handle_create_form_submission()
        return self._render_create_form()

    def _handle_create_form_submission(self):
        """Processes the submitted data for creating a new item."""
        errors = self.form_handler.validate_create(request)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_create_form()

        # Log the raw form data (all values, including multi-selects)
        logger.info(f"Raw form data received for create: {request.form.to_dict(flat=False)}")
        form_data = self._preprocess_form_data(request)
        logger.info(f"Processed submitted data for create: {form_data}")

        result, error = self.item_manager.create_item(form_data)
        if error:
            flash(error, "error")
            return self._render_create_form()

        # Log the newly created database entry (if available)
        if hasattr(result, "to_dict"):
            logger.info(f"Database entry created: {result.to_dict()}")
        else:
            logger.info(f"Database entry created: {result}")
        flash(f"{self.model.__name__} created successfully", "success")
        return result

    def _render_create_form(self):
        """Renders the creation form template."""
        item_dict = {}
        tabs = self.get_tabs_function(item_dict)
        context = ResourceContext.create_context(
            model=self.model,
            blueprint_name=self.blueprint.name,
            item_dict=item_dict,
            tabs=tabs,
            title=f"Create a {self.model.__name__}",
            read_only=False
        )
        return render_safely(self.create_template, context, f"Error rendering create form for {self.model.__name__}")

    def _edit_route(self, item_id: int):
        """Handles requests to edit an existing item.

        Args:
            item_id (int): The ID of the item.
        Returns:
            Response: Rendered edit template.
        """
        self.request_logger.log_request_info(self.model.__name__, "edit", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error or item is None:
            flash("Item not found.", "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))
        if request.method == "POST":
            return self._handle_edit_form_submission(item)
        return self._render_edit_form(item)

    # Add this method to the GenericWebRoutes class in generic.py

    def add_edit_context(self, item, context):
        """
        Adds additional data to the edit context before rendering.
        This method can be overridden by child classes to add custom data.

        Args:
            item: The database item being edited
            context: The template rendering context dictionary
        """
        # Base implementation does nothing
        pass

    def add_edit_context(self, item, context_obj):
        """
        Adds additional data to the edit context before rendering.
        This method can be overridden by child classes to add custom data.

        Args:
            item: The database item being edited
            context_obj: The ResourceContext object for rendering
        """
        # Base implementation does nothing
        pass

    def _render_edit_form(self, item):
        """Renders the form for editing an existing item."""
        item_dict = item.to_dict()
        tabs = self.get_tabs_function(item_dict)

        # Create additional context data (before creating ResourceContext)
        extra_context = {}

        # Call the add_edit_context method to allow child classes to add data
        self.add_edit_context(item, extra_context)

        # Create the ResourceContext with the extra data
        context = ResourceContext.create_context(
            model=self.model,
            blueprint_name=self.blueprint.name,
            item_dict=item_dict,
            tabs=tabs,
            title=f"Edit {self.model.__name__}",
            read_only=False,
            **extra_context  # Include any extra context data
        )

        return render_safely(self.edit_template, context, f"Error rendering edit form for {self.model.__name__}")

    def _handle_edit_form_submission(self, item):
        """Handles submitted form data for editing an existing item."""
        errors = self.form_handler.validate_edit(item, request)
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

    def _delete_route(self, item_id: int):
        """Handles deleting an item by ID.

        Args:
            item_id (int): The ID of the item.
        Returns:
            Response: Redirect to the index page.
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

    def _data_route(self):
        """Handles data table API requests."""
        self.request_logger.log_request_info(self.model.__name__, "data")
        return self.data_handler.handle_data_request()

    def _validate_create_from_request(self, request_obj):
        """Validates form data from the request object for create."""
        return self._validate_create(request_obj.form.to_dict())

    def _validate_edit_from_request(self, item, request_obj):
        """Validates form data from the request object for edit."""
        return self._validate_edit(item, request_obj.form.to_dict())

    def _preprocess_form_data(self, request):
        """
        Converts form data into a dictionary and casts date strings to Python datetime objects.
        Also processes multi-select fields for 'users' and 'companies' to capture list values,
        filtering out any empty strings.
        """
        # Log the raw form data (with all values as lists)
        raw_data = request.form.to_dict(flat=False)
        logger.info(f"Raw form data (flat=False): {raw_data}")

        # Start with the basic form data (first value only for each field)
        form_data = request.form.to_dict()

        # For multi-select or mapping fields, capture all selected values and filter out empty strings.
        if "users" in request.form:
            users_list = request.form.getlist("users")
            form_data["users"] = [u for u in users_list if u]
        if "companies" in request.form:
            companies_list = request.form.getlist("companies")
            form_data["companies"] = [c for c in companies_list if c]

        # Convert 'created_at' to a datetime object if present.
        if "created_at" in form_data and form_data["created_at"]:
            try:
                form_data["created_at"] = datetime.fromisoformat(form_data["created_at"])
            except ValueError:
                logger.error("Invalid format for created_at. Expected ISO format.")
        # Convert 'updated_at' to a datetime object if present.
        if "updated_at" in form_data and form_data["updated_at"]:
            try:
                form_data["updated_at"] = datetime.fromisoformat(form_data["updated_at"])
            except ValueError:
                logger.error("Invalid format for updated_at. Expected ISO format.")
        return form_data
