from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.contact import Contact
from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

contacts_bp = Blueprint("contacts_bp", __name__, url_prefix="/contacts")
contact_service = CRUDService(Contact)
templates = default_crud_templates("Contact")


@contacts_bp.route("/", methods=["GET"])
@use_context(TableContext, entity_table_name="Contact", action="index")
@login_required
def index(context):
    return render_template(templates.index, **context.to_dict())


@contacts_bp.route("/create", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Contact", action="create")
@login_required
def create(context):
    if request.method == "POST":
        try:
            data = request.form.to_dict()
            entity = contact_service.create(data)
            flash("Contact created successfully.", "success")
            return redirect(url_for("contacts_bp.view", entity_id=entity.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.create, **context.to_dict())


@contacts_bp.route("/<int:entity_id>", methods=["GET"])
@use_context(EntityContext, entity_table_name="Contact", action="view")
@login_required
def view(context, entity_id):
    return render_template(templates.view, **context.to_dict())


@contacts_bp.route("/<int:entity_id>/edit", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Contact", action="edit")
@login_required
def edit(context, entity_id):
    if request.method == "POST":
        try:
            entity = contact_service.get_by_id(entity_id)
            contact_service.update(entity, request.form.to_dict())
            flash("Contact updated successfully.", "success")
            return redirect(url_for("contacts_bp.view", entity_id=entity.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.edit, **context.to_dict())


@contacts_bp.route("/<int:entity_id>/delete", methods=["POST"])
@login_required
def delete(entity_id):
    try:
        contact_service.delete(entity_id)
        flash("Contact deleted.", "success")
        return redirect(url_for("contacts_bp.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("contacts_bp.view", entity_id=entity_id))
