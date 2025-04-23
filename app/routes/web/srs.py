from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.srs_service import SRSService
from app.utils.app_logging import get_logger

logger = get_logger()

srs_bp = Blueprint("srs_bp", __name__, url_prefix="/srs")
srs_service = SRSService()
templates = default_crud_templates("SRSItem")


@srs_bp.route("/", methods=["GET"])
@use_context(TableContext, entity_table_name="SRSItem", action="index")
@login_required
def index(context):
    return render_template(templates.index, **context.to_dict())


@srs_bp.route("/create", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="SRSItem", action="create")
@login_required
def create(context):
    if request.method == "POST":
        try:
            ent = srs_service.create(request.form.to_dict())
            flash("SRS item created.", "success")
            return redirect(url_for("srs_bp.view", entity_id=ent.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.create, **context.to_dict())


@srs_bp.route("/<int:entity_id>", methods=["GET"])
@use_context(EntityContext, entity_table_name="SRSItem", action="view")
@login_required
def view(context, entity_id):
    return render_template(templates.view, **context.to_dict())


@srs_bp.route("/<int:entity_id>/edit", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="SRSItem", action="edit")
@login_required
def edit(context, entity_id):
    if request.method == "POST":
        try:
            item = srs_service.get_by_id(entity_id)
            srs_service.update(item, request.form.to_dict())
            flash("SRS item updated.", "success")
            return redirect(url_for("srs_bp.view", entity_id=item.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.edit, **context.to_dict())


@srs_bp.route("/<int:entity_id>/delete", methods=["POST"])
@login_required
def delete(entity_id):
    try:
        srs_service.delete(entity_id)
        flash("SRS item deleted.", "success")
        return redirect(url_for("srs_bp.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("srs_bp.view", entity_id=entity_id))
