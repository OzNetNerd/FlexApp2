from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.opportunity import Opportunity
from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

opportunities_bp = Blueprint("opportunities_bp", __name__, url_prefix="/opportunities")
opportunity_service = CRUDService(Opportunity)
templates = default_crud_templates("Opportunity")


@opportunities_bp.route("/", methods=["GET"])
@use_context(TableContext, entity_table_name="Opportunity", action="index")
@login_required
def index(context):
    return render_template(templates.index, **context.to_dict())


@opportunities_bp.route("/create", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Opportunity", action="create")
@login_required
def create(context):
    if request.method == "POST":
        try:
            ent = opportunity_service.create(request.form.to_dict())
            flash("Opportunity created.", "success")
            return redirect(url_for("opportunities_bp.view", entity_id=ent.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.create, **context.to_dict())


@opportunities_bp.route("/<int:entity_id>", methods=["GET"])
@use_context(EntityContext, entity_table_name="Opportunity", action="view")
@login_required
def view(context, entity_id):
    return render_template(templates.view, **context.to_dict())


@opportunities_bp.route("/<int:entity_id>/edit", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Opportunity", action="edit")
@login_required
def edit(context, entity_id):
    if request.method == "POST":
        try:
            opp = opportunity_service.get_by_id(entity_id)
            opportunity_service.update(opp, request.form.to_dict())
            flash("Opportunity updated.", "success")
            return redirect(url_for("opportunities_bp.view", entity_id=opp.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.edit, **context.to_dict())


@opportunities_bp.route("/<int:entity_id>/delete", methods=["POST"])
@login_required
def delete(entity_id):
    try:
        opportunity_service.delete(entity_id)
        flash("Opportunity deleted.", "success")
        return redirect(url_for("opportunities_bp.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("opportunities_bp.view", entity_id=entity_id))
