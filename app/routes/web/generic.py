from dataclasses import dataclass, field
from typing import Optional, List, Type
from flask import request, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
import logging
import traceback

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
    view_template: Optional[str] = "base/create_view_edit.html"
    create_template: Optional[str] = "base/create_view_edit.html"
    edit_template: Optional[str] = "base/create_view_edit.html"
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
        form_handler.validate_create = self._validate_create
        form_handler.validate_edit = self._validate_edit
        return form_handler

    def _register_routes(self):
        self.blueprint.add_url_rule(
            "/", "index", login_required(self._index_route), methods=["GET"]
        )
        self.blueprint.add_url_rule(
            "/<int:item_id>", "view", login_required(self._view_route), methods=["GET"]
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

    def _view_route(self, item_id):
        self.request_logger.log_request_info(self.model.__name__, "view", item_id)
        item, error = self.item_manager.get_item_by_id(item_id)
        if error:
            flash(error, "error")
            return redirect(url_for(f"{self.blueprint.name}.index"))

        fields = self.form_handler.build_fields(item)
        context = self.form_handler.prepare_form_context(
            title=f"View {self.model.__name__}",
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

    def _create_route(self):
        self.request_logger.log_request_info(self.model.__name__, "create")
        if request.method == "POST":
            return self._handle_create_form_submission()
        return self._render_create_form()

    def _handle_create_form_submission(self):
        form_data = request.form.to_dict()
        errors = self.form_handler.validate_create(form_data)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_create_form()

        result, error = self.item_manager.create_item(form_data)
        if error:
            flash(error, "error")
            return self._render_create_form()
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
        form_data = request.form.to_dict()
        errors = self.form_handler.validate_edit(item, form_data)
        if errors:
            for e in errors:
                flash(e, "error")
            return self._render_edit_form(item)

        result, error = self.item_manager.update_item(item, form_data)
        if error:
            flash(error, "error")
            return self._render_edit_form(item)
        return result

    def _render_create_form(self):
        fields = self.json_validator.ensure_json_serializable(
            self.form_handler.build_fields()
        )
        context = self.form_handler.prepare_form_context(
            title=f"Create {self.model.__name__}",
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
        return redirect(url_for(f"{self.blueprint.name}.index"))

    def _data_route(self):
        self.request_logger.log_request_info(self.model.__name__, "data")
        return self.data_handler.handle_data_request()

    def _validate_create(self, form_data):
        return [
            f"{field} is required"
            for field in self.required_fields
            if not form_data.get(field)
        ]

    def _validate_edit(self, item, form_data):
        return self._validate_create(form_data)

    def add_view_context(self, item, context):
        logger.debug(
            f"Generic add_view_context for {self.model.__name__} with ID {item.id}"
        )
        crisp_type = self.model.__tablename__.rstrip("s")
        relationship = next(
            (
                rel
                for rel in getattr(item, "relationships", [])
                if rel.user_id == current_user.id
            ),
            None,
        )
        context["relationship"] = relationship
        context["crisp_scores"] = (
            relationship.crisp_scores.order_by(CRISPScore.created_at.desc()).all()
            if relationship
            else []
        )
        context["crisp_type"] = crisp_type
        if hasattr(item, "notes"):
            context["notes_model"] = Note
