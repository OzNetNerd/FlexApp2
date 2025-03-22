from dataclasses import dataclass, field
from typing import Optional, List, Type
from flask import request, redirect, url_for, flash, Blueprint, json
import logging
import traceback
from routes.base.crud_base import CRUDRoutesBase
from services.crud_service import CRUDService

from routes.base.components.template_renderer import render_safely
from routes.base.components.json_validator import JSONValidator
from routes.base.components.request_logger import RequestLogger
from routes.base.components.table_config_manager import TableConfigManager
from routes.base.components.data_route_handler import DataRouteHandler
from routes.base.components.form_handler import FormHandler
from routes.base.components.item_manager import ItemManager
from models import Company

logger = logging.getLogger(__name__)

GENERIC_TEMPLATE = 'base-page.html'


@dataclass
class GenericWebRoutes(CRUDRoutesBase):
    """
    Handles web UI routes for CRUD operations.
    Returns HTML templates for browser users.
    Uses composition with specialized handler classes.
    """
    blueprint: Blueprint
    model: Type
    service: CRUDService = field(default_factory=CRUDService)
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    index_template: str = GENERIC_TEMPLATE
    view_template: Optional[str] = None
    create_template: Optional[str] = None
    edit_template: Optional[str] = None
    api_url_prefix: Optional[str] = None

    def __post_init__(self):
        """
        Initialize handlers and register web routes.
        """
        super().__post_init__()

        prefix = self.blueprint.name.replace('_bp', '')
        template_file_path = f"{prefix}/create_view_edit.html"

        if not self.create_template:
            self.create_template = template_file_path
        if not self.edit_template:
            self.edit_template = template_file_path
        if not self.view_template:
            self.view_template = template_file_path

        # Initialize handlers using composition
        self.json_validator = JSONValidator()
        self.request_logger = RequestLogger()
        self.table_config_manager = TableConfigManager(self.json_validator)
        self.data_handler = DataRouteHandler(self.service, self.model, self.json_validator)
        self.item_manager = ItemManager(self.model, self.service, self.blueprint.name)
        self.form_handler = self._create_form_handler()

        # Register routes
        self._register_routes()
        logger.debug(f"Web CRUD routes registered for {self.model.__name__} model.")

    def _create_form_handler(self):
        """Create and initialize form handler with model-specific logic."""
        form_handler = FormHandler(self.model, self.service, self.json_validator)
        # Override methods with our implementations
        form_handler.build_fields = self._build_fields
        form_handler.validate_create = self._validate_create
        form_handler.validate_edit = self._validate_edit
        return form_handler

    def _get_template_context(self, **kwargs):
        """Provide context variables used by all templates (overridable by child classes)."""
        context = kwargs.get("context", {})
        context['companies'] = Company.query.order_by(Company.name).all()
        context['use_autocomplete'] = True
        return context

    def _register_routes(self):
        """
        Register standard web UI routes.
        """
        logger.debug(f"Registering web routes for {self.model.__name__}.")

        # Index page
        self.blueprint.add_url_rule(
            '/',
            'index',
            self._index_route,
            methods=['GET']
        )
        # View page
        self.blueprint.add_url_rule(
            '/<int:item_id>',
            'view',
            self._view_route,
            methods=['GET']
        )
        # Create page
        self.blueprint.add_url_rule(
            '/create',
            'create',
            self._create_route,
            methods=['GET', 'POST']
        )
        # Edit page
        self.blueprint.add_url_rule(
            '/<int:item_id>/edit',
            'edit',
            self._edit_route,
            methods=['GET', 'POST']
        )
        # Delete action
        self.blueprint.add_url_rule(
            '/<int:item_id>/delete',
            'delete',
            self._delete_route,
            methods=['POST']
        )

        # Data API route (temporary until fully migrated to API endpoints)
        self.blueprint.add_url_rule(
            '/data',
            'data',
            self._data_route,
            methods=['GET']
        )

    def _determine_data_url(self):
        """Determine the appropriate data URL based on API configuration."""
        if self.api_url_prefix:
            # Use the API endpoint
            data_url = f"{self.api_url_prefix}/{self.model.__tablename__}"
            logger.debug(f"Using API data URL: {data_url}")
        else:
            # Fall back to the web UI data route
            data_url = url_for(f'{self.blueprint.name}.data')
            logger.debug(f"Using web UI data URL: {data_url}")
        return data_url

    def _prepare_index_context(self, table_config):
        """Prepare the context for the index template."""
        data_url = self._determine_data_url()

        context = {
            'page_type': "index",
            'title': f"{self.model.__name__}s",
            'table_config': table_config,
            'table_id': f"{self.model.__tablename__}_table",
            'data_url': data_url,
            'entity_name': self.model.__name__,
            'add_url': url_for(f'{self.blueprint.name}.create'),
            'columns': table_config.get('columns', [])
        }

        # Log context details
        logger.debug(f"Template context keys: {list(context.keys())}")
        logger.debug(f"Context values: data_url={context['data_url']}, table_id={context['table_id']}")

        return context

    def _index_route(self):
        """Render index page with table of items."""
        self.request_logger.log_request_info(self.model.__name__, 'index')

        # Get table configuration
        table_config = self.table_config_manager.get_table_config(self.model.__tablename__)

        # Prepare template context
        context = self._prepare_index_context(table_config)

        # Log context contents
        logger.debug(f"Context for {self.model.__name__} index: {context}")

        # Render template
        return render_safely(
            self.index_template,
            context,
            f"Error rendering {self.model.__name__} index"
        )

    def _prepare_view_context(self, item):
        """Prepare the context for the view template."""
        # Create the initial context
        context = {
            'page_type': "view",
            'title': f"View {self.model.__name__}",
            'item': item,
            self.model.__tablename__.rstrip('s'): item  # Add item with model name as key (singular)
        }

        # Allow subclasses to add additional context
        try:
            self.add_view_context(item, context)
            logger.debug(f"Added additional context for {self.model.__name__}")
        except Exception as e:
            logger.error(f"Error in add_view_context: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

        # Ensure the context is JSON serializable
        for key, value in list(context.items()):
            try:
                if key != 'item' and key != self.model.__tablename__.rstrip('s'):
                    json.dumps({key: value})
            except TypeError:
                context[key] = self.json_validator.ensure_json_serializable(value)

        return context

    def _view_route(self, item_id):
        """Render view page for a single item."""
        self.request_logger.log_request_info(self.model.__name__, 'view', item_id)

        # Get the item
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, 'error')
            return redirect(url_for(f'{self.blueprint.name}.index'))

        # Prepare template context
        context = self._prepare_view_context(item)

        # Render template
        return render_safely(
            self.view_template,
            context,
            f"Error viewing {self.model.__name__} with id {item_id}"
        )

    def add_view_context(self, item, context):
        """Hook for subclasses to add additional context to view template."""
        logger.debug(f"Base add_view_context called for {self.model.__name__}.")
        pass

    def _handle_create_form_submission(self):
        """Process create form submission."""
        form_data = request.form.to_dict()
        logger.debug(f"Received form data with {len(form_data)} fields")

        # Validate form data
        validation_errors = self.form_handler.validate_create(form_data)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            logger.debug("Validation errors found, rendering create form.")
            return self._render_create_form()

        # Create the item
        result, error = self.item_manager.create_item(form_data)
        if error:
            flash(error, 'error')
            return self._render_create_form()
        return result

    def _create_route(self):
        """Render create form or process form submission."""
        self.request_logger.log_request_info(self.model.__name__, 'create')

        if request.method == 'POST':
            return self._handle_create_form_submission()

        logger.debug(f"GET request for create form, rendering create template")
        return self._render_create_form()

    def _handle_edit_form_submission(self, item):
        """Process edit form submission."""
        form_data = request.form.to_dict()
        logger.debug(f"Received {len(form_data)} form fields for edit")

        # Validate form data
        validation_errors = self.form_handler.validate_edit(item, form_data)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return self._render_edit_form(item)

        # Update the item
        result, error = self.item_manager.update_item(item, form_data)
        if error:
            flash(error, 'error')
            return self._render_edit_form(item)
        return result

    def _edit_route(self, item_id):
        """Render edit form or process form submission."""
        self.request_logger.log_request_info(self.model.__name__, 'edit', item_id)

        # Get the item
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, 'error')
            return redirect(url_for(f'{self.blueprint.name}.index'))

        if request.method == 'POST':
            return self._handle_edit_form_submission(item)

        logger.debug(f"GET request for edit form, rendering edit template for item {item_id}")
        return self._render_edit_form(item)

    def _delete_route(self, item_id):
        """Process delete request."""
        self.request_logger.log_request_info(self.model.__name__, 'delete', item_id)

        # Get the item
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, 'error')
            return redirect(url_for(f'{self.blueprint.name}.index'))

        # Delete the item
        success, error = self.item_manager.delete_item(item)
        if error:
            flash(error, 'error')

        return redirect(url_for(f'{self.blueprint.name}.index'))

    def _render_create_form(self):
        """Render the create form with dynamic fields."""
        logger.debug(f"Rendering create form for {self.model.__name__}.")
        try:
            fields = self.form_handler.build_fields()
            logger.debug(f"Built {len(fields)} fields for create form")

            # Ensure fields are JSON serializable
            fields = self.json_validator.ensure_json_serializable(fields)

            context = self.form_handler.prepare_form_context(
                title=f"Create {self.model.__name__}",
                submit_url=url_for(f'{self.blueprint.name}.create'),
                cancel_url=url_for(f'{self.blueprint.name}.index'),
                fields=fields,
                button_text=f"Create {self.model.__name__}",
                read_only=False,  # <- required for the shared form
            )

            context.update(self._get_template_context(context=context))  # Adds extras like companies list

            return render_safely(
                self.create_template,
                context,
                f"Error rendering create form for {self.model.__name__}"
            )
        except Exception as e:
            logger.error(f"Error preparing create form: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            flash(f'Error rendering create form: {str(e)}', 'error')
            return redirect(url_for(f'{self.blueprint.name}.index'))

    def _render_edit_form(self, item):
        """Render the edit form with dynamic fields pre-populated."""
        logger.debug(f"Rendering edit form for {self.model.__name__} with id {item.id}.")
        try:
            fields = self.form_handler.build_fields(item)
            logger.debug(f"Built {len(fields)} fields for edit form")

            # Ensure fields are JSON serializable
            fields = self.json_validator.ensure_json_serializable(fields)

            context = self.form_handler.prepare_form_context(
                title=f"Edit {self.model.__name__}",
                submit_url=url_for(f'{self.blueprint.name}.edit', item_id=item.id),
                cancel_url=url_for(f'{self.blueprint.name}.view', item_id=item.id),
                edit_url=url_for(f'{self.blueprint.name}.edit', item_id=item.id),
                fields=fields,
                button_text=f"Update {self.model.__name__}",
                item=item,
                read_only=False  # Set to True if rendering for view only
            )

            return render_safely(
                self.edit_template or self.index_template,
                context,
                f"Error rendering edit form for {self.model.__name__}"
            )
        except Exception as e:
            logger.error(f"Error preparing edit form: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            flash(f'Error rendering edit form: {str(e)}', 'error')
            return redirect(url_for(f'{self.blueprint.name}.index'))

    def _data_route(self):
        """Data route for AG Grid with pagination and sorting."""
        self.request_logger.log_request_info(self.model.__name__, 'data')
        return self.data_handler.handle_data_request()

    # These methods need to be implemented in the main class
    # as they're specific to the model and will be passed to the form handler

    def _build_fields(self, item=None):
        """Build form fields based on model properties."""
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _build_fields method")

    def _validate_create(self, form_data):
        """Validate form data for create operation."""
        # Basic validation, should be extended by subclasses
        errors = []
        for field in self.required_fields:
            if field not in form_data or not form_data[field]:
                errors.append(f"{field} is required")
        return errors

    def _validate_edit(self, item, form_data):
        """Validate form data for edit operation."""
        # Basic validation, should be extended by subclasses
        return self._validate_create(form_data)