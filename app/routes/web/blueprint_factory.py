# app/routes/web/blueprint_factory.py

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()


# Simplified version of create_crud_blueprint
def create_crud_blueprint(model_class):
    blueprint_name = f"{model_class.__tablename__}_bp"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=f"/{model_class.__tablename__}")
    service = CRUDService(model_class)
    templates = default_crud_templates(model_class.__entity_name__)

    @blueprint.route("/", methods=["GET"])
    @use_context(TableContext, model_class=model_class, action="index")
    @login_required
    def index(context):
        return render_template(templates.index, **context.to_dict())

    # Other routes similar to your existing code...

    return blueprint