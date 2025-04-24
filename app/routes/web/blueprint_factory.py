# app/routes/web/blueprint_factory.py

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()


def create_crud_blueprint(model_class):
    """Factory function to create a complete CRUD blueprint for any model."""

    # Get entity information from model
    entity_name = model_class.__entity_name__
    entity_plural = model_class.__entity_plural__.capitalize()
    blueprint_name = f"{model_class.__tablename__}_bp"
    url_prefix = f"/{model_class.__tablename__}"

    # Create blueprint and service
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=url_prefix)
    service = CRUDService(model_class)
    templates = default_crud_templates(entity_name)

    # Define route handlers
    @blueprint.route("/", methods=["GET"])
    @use_context(TableContext, entity_table_name=entity_name, action="index")
    @login_required
    def index(context):
        return render_template(templates.index, **context.to_dict())

    @blueprint.route("/create", methods=["GET", "POST"])
    @use_context(EntityContext, entity_table_name=entity_name, action="create")
    @login_required
    def create(context):
        if request.method == "POST":
            try:
                entity = service.create(request.form.to_dict())
                flash(f"{entity_name} created.", "success")
                return redirect(url_for(f"{blueprint_name}.view", entity_id=entity.id))
            except Exception as e:
                flash(str(e), "danger")
        return render_template(templates.create, **context.to_dict())

    @blueprint.route("/<int:entity_id>", methods=["GET"])
    @use_context(EntityContext, entity_table_name=entity_name, action="view")
    @login_required
    def view(context, entity_id):
        return render_template(templates.view, **context.to_dict())

    @blueprint.route("/<int:entity_id>/edit", methods=["GET", "POST"])
    @use_context(EntityContext, entity_table_name=entity_name, action="edit")
    @login_required
    def edit(context, entity_id):
        if request.method == "POST":
            try:
                entity = service.get_by_id(entity_id)
                service.update(entity, request.form.to_dict())
                flash(f"{entity_name} updated.", "success")
                return redirect(url_for(f"{blueprint_name}.view", entity_id=entity.id))
            except Exception as e:
                flash(str(e), "danger")
        return render_template(templates.edit, **context.to_dict())

    @blueprint.route("/<int:entity_id>/delete", methods=["POST"])
    @login_required
    def delete(entity_id):
        try:
            service.delete(entity_id)
            flash(f"{entity_name} deleted.", "success")
            return redirect(url_for(f"{blueprint_name}.index"))
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for(f"{blueprint_name}.view", entity_id=entity_id))

    return blueprint