from dataclasses import dataclass, field
from typing import Optional, List, Type
from flask import request, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
import logging

from app.services.crud_service import CRUDService
from app.routes.base.crud_base import CRUDRoutesBase
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.json_validator import JSONValidator
from app.routes.base.components.request_logger import RequestLogger
from app.routes.base.components.table_config_manager import TableConfigManager
from app.routes.base.components.data_route_handler import DataRouteHandler
from app.routes.base.components.form_handler import FormHandler, ResourceContext, IndexContext
from app.routes.base.components.item_manager import ItemManager
from app.models import Company, CRISPScore, Note

logger = logging.getLogger(__name__)
GENERIC_TEMPLATE = "page.html"


@dataclass
class GenericWebRoutes(CRUDRoutesBase):
    """Generic web routes for CRUD operations.

    This class implements generic CRUD web routes for a given model using Flask.

    Attributes:
        model (Type): The model class for which CRUD operations are performed.
        blueprint (Blueprint): The Flask blueprint to register routes.
        required_fields (List[str]): List of required field names.
        unique_fields (List[str]): List of field names that must be unique.
        index_template (str): Template used for rendering the index page.
        view_template (Optional[str]): Template used for rendering the view page.
        create_template (Optional[str]): Template used for rendering the create page.
        edit_template (Optional[str]): Template used for rendering the edit page.
        api_url_prefix (Optional[str]): URL prefix for the API endpoints.
    """
    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    index_template: str = GENERIC_TEMPLATE
    view_template: Optional[str] = "shared/view.html"
    create_template: Optional[str] = "shared/create.html"
    edit_template: Optional[str] = "shared/edit.html"
    api_url_prefix: Optional[str] = None

    def __post_init__(self):
        """Post initialization processing.

        Initializes additional components (CRUD service, JSON validator, etc.),
        creates the form handler, registers the web routes, and logs the registration.
        """
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
        """Creates and configures the form handler.

        If a `_build_fields` method is defined, it assigns it to the form handler.
        Also sets the validation methods for create and edit operations.

        Returns:
            FormHandler: The configured form handler instance.
        """
        form_handler = FormHandler(self.model, self.service, self.json_validator)
        # if hasattr(self, "_build_fields"):
        #     form_handler.build_fields = self._build_fields
        form_handler.validate_create = self._validate_create_from_request
        form_handler.validate_edit = self._validate_edit_from_request
        return form_handler

    def _register_routes(self):
        """Registers all necessary web routes with the blueprint.

        Sets up the URL rules for index, view, create, edit, delete, and data routes.
        """
        self.blueprint.add_url_rule("/", "index", login_required(self._index_route), methods=["GET"])
        self.blueprint.add_url_rule("/<int:item_id>", "view", login_required(self._view_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/create", "create", login_required(self._create_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/edit", "edit", login_required(self._edit_route), methods=["GET", "POST"])
        self.blueprint.add_url_rule("/<int:item_id>/delete", "delete", login_required(self._delete_route), methods=["POST"])
        self.blueprint.add_url_rule("/data", "data", login_required(self._data_route), methods=["GET"])

    # def _get_template_context(self, **kwargs) -> dict:
    #     """Retrieves the context for rendering a template.
    #
    #     Prepares the context dictionary used for template rendering, including
    #     a list of companies, autocomplete usage flag, and model field order.
    #
    #     Args:
    #         **kwargs: Arbitrary keyword arguments that may include an existing context.
    #
    #     Returns:
    #         dict: A context dictionary with keys 'companies', 'use_autocomplete', and 'fields'.
    #     """
    #     context = kwargs.get("context", {})
    #     context["companies"] = Company.query.order_by(Company.name).all()
    #     context["use_autocomplete"] = True
    #     context["section"] = ""
    #     context["fields"] = self.model.__tabs__
    #     return context

    def _determine_data_url(self) -> str:
        """Determines the URL for data API requests.

        Returns:
            str: The URL to be used for data requests.
        """
        return f"{self.api_url_prefix}/{self.model.__tablename__}" if self.api_url_prefix else url_for(f"{self.blueprint.name}.data")

    def _prepare_page_index_context(self, table_config: dict) -> dict:
        """Prepares the context for the index page.

        Args:
            table_config (dict): The configuration for the table to be rendered.

        Returns:
            dict: A dictionary with context data for the index page.
        """
        data_url = self._determine_data_url()
        return IndexContext(
            page_type="index",
            title=f"{self.model.__name__}s",
            table_config=table_config,
            table_id=f"{self.model.__tablename__}_table",
            data_url=data_url,
            entity_name=self.model.__name__,
            add_url=url_for(f"{self.blueprint.name}.create"),
            columns=table_config.get("columns", []),
        )

    def _index_route(self):
        """Handles requests to the index route.

        Logs the request information, retrieves table configuration,
        prepares the context, and renders the index template.

        Returns:
            Response: The rendered index page or an error response.
        """
        self.request_logger.log_request_info(self.model.__name__, "index")
        table_config = self.table_config_manager.get_table_config(self.model.__tablename__)
        context = self._prepare_page_index_context(table_config)
        logger.debug(f"Rendering index template: {self.index_template}")
        return render_safely(self.index_template, context, f"Error rendering {self.model.__name__} index")

    @staticmethod
    def _get_item_display_name(item) -> str:
        """Retrieves a user-friendly display name for an item.

        Attempts to use one of the common attributes such as 'name', 'title', 'email', or 'username'.
        If not available, it falls back to combining 'first_name' and 'last_name', or the item ID.

        Args:
            item: The item whose display name is needed.

        Returns:
            str: The display name for the item.
        """
        for attr in ["name", "title", "email", "username"]:
            if hasattr(item, attr) and getattr(item, attr):
                return getattr(item, attr)
        if hasattr(item, "first_name") and hasattr(item, "last_name"):
            return f"{item.first_name} {item.last_name}".strip()
        return str(item.id)

    def _view_route(self, item_id):
        """Handles viewing an individual item.

        Fetches the item using the provided ID, logs the request,
        and processes GET and POST methods appropriately.

        Args:
            item_id (int): The identifier of the item to view.

        Returns:
            Response: The rendered view page or a redirect if an error occurs.
        """
        logger.debug(f"Request to view item with ID {item_id} for model {self.model.__name__}")
        self.request_logger.log_request_info(self.model.__name__, "view", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            logger.error(f"Error retrieving item with ID {item_id}: {error}")
            flash(error, "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))

        logger.debug(f"Item with ID {item_id} fetched successfully: {item}")
        if request.method == "POST":
            logger.debug(f"POST request received for item with ID {item_id}. Handling view post.")
            return self._handle_view_post(item)

        resource_contex = ResourceContext(
            title="Viewing",
            model_name=self.model.__name__,
            item_name=self._get_item_display_name(item),
            submit_url="",
            cancel_url=url_for(f"{self.blueprint.name}.index"),
            tabs=self.model.__tabs__,
            id=getattr(item, "id", None),
            item=item,
            read_only=True
        )

        logger.debug(f"Rendering view template: {self.view_template}")
        return render_safely(self.view_template, resource_contex, f"Error viewing {self.model.__name__} with id {item_id}")

    def _handle_view_post(self, item):
        """Processes POST requests on the view route to add a note.

        Retrieves note content from the form, creates a new note associated with the item,
        and attempts to save it. Appropriate flash messages are set based on success or failure.

        Args:
            item: The item to which the note will be added.

        Returns:
            Response: A redirect to the view page of the item.
        """
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
        """Handles requests to the create route.

        Logs the create request and processes GET and POST methods.
        For POST requests, it handles form submission; otherwise, it renders the create form.

        Returns:
            Response: The rendered create form page or the result of form submission.
        """
        self.request_logger.log_request_info(self.model.__name__, "create")
        if request.method == "POST":
            return self._handle_create_form_submission()
        return self._render_create_form()

    def _handle_create_form_submission(self):
        """Processes the submission of the create form.

        Validates the form data, creates a new item if validation passes,
        and sets flash messages based on the outcome.

        Returns:
            Response: The rendered create form with errors or the result of a successful creation.
        """
        errors = self.form_handler.validate_create(request)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_create_form()

        form_data = self._preprocess_form_data(request)
        result, error = self.item_manager.create_item(form_data)
        if error:
            flash(error, "error")
            return self._render_create_form()
        flash(f"{self.model.__name__} created successfully", "success")
        return result

    def _render_create_form(self):
        """Renders the form for creating a new item.

        Prepares the form context, ensures JSON serializability of fields,
        and renders the create template.

        Returns:
            Response: The rendered create form page.
        """
        context = {
            "title": f"Create a {self.model.__name__}",
            "submit_url": url_for(f"{self.blueprint.name}.create"),
            "cancel_url": url_for(f"{self.blueprint.name}.index"),
            "fields": "",
            "section": "",
            "item": "item",
            "id": "id",
            "button_text": f"Create {self.model.__name__}",
            "read_only": False,
        }

        # context.update(self._get_template_context(context=context))
        logger.debug(f"Rendering create template: {self.create_template}")
        return render_safely(self.create_template, context, f"Error rendering create form for {self.model.__name__}")

    def _edit_route(self, item_id):
        """Handles requests to the edit route for an item.

        Retrieves the item by ID, logs the edit request,
        and processes GET and POST methods for editing.

        Args:
            item_id (int): The identifier of the item to edit.

        Returns:
            Response: The rendered edit form page or the result of form submission.
        """
        self.request_logger.log_request_info(self.model.__name__, "edit", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error or item is None:
            flash("Item not found.", "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))

        if request.method == "POST":
            return self._handle_edit_form_submission(item)

        return self._render_edit_form(item)

    def _render_edit_form(self, item):
        """Renders the edit form for the specified item.

        Prepares the form context with the current item data and renders the edit template.

        Args:
            item: The item to be edited.

        Returns:
            Response: The rendered edit form page.
        """
        logger.info(f'this is item - \n{item}')
        context = {
            "title": f"Edit {self.model.__name__}",
            "submit_url": url_for(f"{self.blueprint.name}.edit", item_id=item.id),
            "cancel_url": url_for(f"{self.blueprint.name}.index"),
            "fields": "",
            "section": "",
            "id": "id",
            "button_text": f"Update {self.model.__name__}",
            "read_only": False,
        }

        # context.update(self._get_template_context(context=context))
        logger.debug(f"Rendering edit template: {self.edit_template}")
        return render_safely(self.edit_template, context, f"Error rendering edit form for {self.model.__name__}")

    def _handle_edit_form_submission(self, item):
        """Processes the submission of the edit form for an item.

        Validates the submitted form data, updates the item if valid,
        and sets appropriate flash messages based on the outcome.

        Args:
            item: The item being edited.

        Returns:
            Response: The rendered edit form page with errors or the result of a successful update.
        """
        errors = self.form_handler.validate_edit(item, request)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_edit_form(item)

        form_data = self._preprocess_form_data(request)
        result, error = self.item_manager.update_item(item, form_data)
        if error:
            flash(error, "error")
            return self._render_edit_form(item)
        flash(f"{self.model.__name__} updated successfully", "success")
        return result

    def _delete_route(self, item_id):
        """Handles the deletion of an item.

        Logs the delete request, attempts to delete the item,
        and flashes success or error messages accordingly.

        Args:
            item_id (int): The identifier of the item to delete.

        Returns:
            Response: A redirect to the index page.
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
        """Handles requests for data retrieval.

        Logs the data request and delegates processing to the data handler.

        Returns:
            Response: The data response for API requests.
        """
        self.request_logger.log_request_info(self.model.__name__, "data")
        return self.data_handler.handle_data_request()

    def _validate_create_from_request(self, request_obj):
        """Validates form data for creating a new item from the request.

        Args:
            request_obj: The Flask request object containing form data.

        Returns:
            Any: The result of the create validation process.
        """
        return self._validate_create(request_obj.form.to_dict())

    def _validate_edit_from_request(self, item, request_obj):
        """Validates form data for editing an item from the request.

        Args:
            item: The item being edited.
            request_obj: The Flask request object containing form data.

        Returns:
            Any: The result of the edit validation process.
        """
        return self._validate_edit(item, request_obj)