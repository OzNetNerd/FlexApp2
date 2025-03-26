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
from app.routes.base.components.form_handler import FormHandler
from app.routes.base.components.item_manager import ItemManager
from app.models import Company, CRISPScore, Note

logger = logging.getLogger(__name__)
GENERIC_TEMPLATE = "page.html"


@dataclass
class GenericWebRoutes(CRUDRoutesBase):
    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    index_template: str = GENERIC_TEMPLATE
    view_template: Optional[str] = "view.html"
    create_template: Optional[str] = "create.html"
    edit_template: Optional[str] = "edit.html"
    api_url_prefix: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.service = CRUDService(self.model)

        self.json_validator = JSONValidator()
        self.request_logger = RequestLogger()
        self.table_config_manager = TableConfigManager(self.json_validator)
        self.data_handler = DataRouteHandler(
            self.service, self.model, self.json_validator
        )
        self.item_manager = ItemManager(self.model, self.service, self.blueprint.name)
        self.form_handler = self._create_form_handler()

        self._register_routes()
        logger.debug(f"Web CRUD routes registered for {self.model.__name__} model.")

    def _create_form_handler(self):
        form_handler = FormHandler(self.model, self.service, self.json_validator)
        if hasattr(self, "_build_fields"):
            form_handler.build_fields = self._build_fields
        form_handler.validate_create = self._validate_create_from_request
        form_handler.validate_edit = self._validate_edit_from_request
        return form_handler

    def _register_routes(self):
        self.blueprint.add_url_rule(
            "/", "index", login_required(self._index_route), methods=["GET"]
        )
        self.blueprint.add_url_rule(
            "/<int:item_id>", "view", login_required(self._view_route), methods=["GET", "POST"]
        )
        self.blueprint.add_url_rule(
            "/create",
            "create",
            login_required(self._create_route),
            methods=["GET", "POST"],
        )
        self.blueprint.add_url_rule(
            "/<int:item_id>/edit",
            "edit",
            login_required(self._edit_route),
            methods=["GET", "POST"],
        )
        self.blueprint.add_url_rule(
            "/<int:item_id>/delete",
            "delete",
            login_required(self._delete_route),
            methods=["POST"],
        )
        self.blueprint.add_url_rule(
            "/data", "data", login_required(self._data_route), methods=["GET"]
        )

    def _get_template_context(self, **kwargs):
        context = kwargs.get("context", {})
        context["companies"] = Company.query.order_by(Company.name).all()
        context["use_autocomplete"] = True
        return context

    def _determine_data_url(self):
        return (
            f"{self.api_url_prefix}/{self.model.__tablename__}"
            if self.api_url_prefix
            else url_for(f"{self.blueprint.name}.data")
        )

    def _prepare_index_context(self, table_config):
        data_url = self._determine_data_url()
        return {
            "page_type": "index",
            "title": f"{self.model.__name__}s",
            "table_config": table_config,
            "table_id": f"{self.model.__tablename__}_table",
            "data_url": data_url,
            "entity_name": self.model.__name__,
            "add_url": url_for(f"{self.blueprint.name}.create"),
            "columns": table_config.get("columns", []),
        }

    def _index_route(self):
        self.request_logger.log_request_info(self.model.__name__, "index")
        table_config = self.table_config_manager.get_table_config(
            self.model.__tablename__
        )
        context = self._prepare_index_context(table_config)
        return render_safely(
            self.index_template, context, f"Error rendering {self.model.__name__} index"
        )

    def _get_item_display_name(self, item):
        for attr in ["name", "title", "email", "username"]:
            if hasattr(item, attr) and getattr(item, attr):
                return getattr(item, attr)
        if hasattr(item, "first_name") and hasattr(item, "last_name"):
            return f"{item.first_name} {item.last_name}".strip()
        return str(item.id)

    def _view_route(self, item_id):
        self.request_logger.log_request_info(self.model.__name__, "view", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))

        if request.method == "POST":
            # Optional: handle comment submission, audit log, etc.
            return self._handle_view_post(item)

        fields = self.form_handler.build_fields(item)
        context = self.form_handler.prepare_form_context(
            # title=f"View {self.model.__name__}: {getattr(item, 'name', item.id)}",
            title=f"Viewing {self.model.__name__}: {self._get_item_display_name(item)}",
            submit_url="",
            cancel_url=url_for(f"{self.blueprint.name}.index"),
            fields=fields,
            item=item,
            read_only=True,
        )
        context.update(self._get_template_context(context=context))
        return render_safely(
            self.view_template,
            context,
            f"Error viewing {self.model.__name__} with id {item_id}",
        )

    def _handle_view_post(self, item):
        note_content = request.form.get("note")
        if not note_content:
            flash("Note content is required.", "error")
            return redirect(url_for(f"{self.blueprint.name}.view", item_id=item.id))

        note = Note(
            content=note_content,
            user_id=current_user.id,
            parent_type=self.model.__name__,
            parent_id=item.id,
        )
        try:
            note.save()  # assuming your Note model has a `save()` method
            flash("Note added successfully", "success")
        except Exception as e:
            logger.exception(f"Error saving note: {e}")
            flash("Failed to save note", "error")

        return redirect(url_for(f"{self.blueprint.name}.view", item_id=item.id))

    def _create_route(self):
        self.request_logger.log_request_info(self.model.__name__, "create")
        if request.method == "POST":
            return self._handle_create_form_submission()
        return self._render_create_form()

    def _handle_create_form_submission(self):
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

    def _edit_route(self, item_id):
        self.request_logger.log_request_info(self.model.__name__, "edit", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))
        if request.method == "POST":
            return self._handle_edit_form_submission(item)
        return self._render_edit_form(item)

    def _handle_edit_form_submission(self, item):
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

    def _render_create_form(self):
        fields = self.json_validator.ensure_json_serializable(
            self.form_handler.build_fields()
        )
        context = self.form_handler.prepare_form_context(
            title=f"Create a {self.model.__name__}",
            submit_url=url_for(f"{self.blueprint.name}.create"),
            cancel_url=url_for(f"{self.blueprint.name}.index"),
            fields=fields,
            button_text=f"Create {self.model.__name__}",
            read_only=False,
        )
        context.update(self._get_template_context(context=context))
        return render_safely(
            self.create_template,
            context,
            f"Error rendering create form for {self.model.__name__}",
        )

    def _render_edit_form(self, item):
        fields = self.json_validator.ensure_json_serializable(
            self.form_handler.build_fields(item)
        )
        context = self.form_handler.prepare_form_context(
            title=f"Edit {self.model.__name__}",
            submit_url=url_for(f"{self.blueprint.name}.edit", item_id=item.id),
            cancel_url=url_for(f"{self.blueprint.name}.index"),
            fields=fields,
            button_text=f"Update {self.model.__name__}",
            read_only=False,
        )
        context.update(self._get_template_context(context=context))
        return render_safely(
            self.edit_template,
            context,
            f"Error rendering edit form for {self.model.__name__}",
        )

    def _delete_route(self, item_id):
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
        self.request_logger.log_request_info(self.model.__name__, "data")
        return self.data_handler.handle_data_request()

    def _validate_create_from_request(self, request_obj):
        return self._validate_create(request_obj.form.to_dict())

    def _validate_edit_from_request(self, item, request_obj):
        return self._validate_edit(item, request_obj)
