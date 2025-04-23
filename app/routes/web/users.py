from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import User
from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.user_service import UserService
from app.utils.app_logging import get_logger

logger = get_logger()

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
user_service = UserService(User)
templates = default_crud_templates("User")


@users_bp.route("/", methods=["GET"])
@use_context(TableContext, entity_table_name="User", action="index")
@login_required
def index(context):
    return render_template(templates.index, **context.to_dict())


@users_bp.route("/create", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="User", action="create")
@login_required
def create(context):
    if request.method == "POST":
        try:
            ent = user_service.create(request.form.to_dict())
            flash("User created.", "success")
            return redirect(url_for("users_bp.view", entity_id=ent.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.create, **context.to_dict())


@users_bp.route("/<int:entity_id>", methods=["GET"])
@use_context(EntityContext, entity_table_name="User", action="view")
@login_required
def view(context, entity_id):
    return render_template(templates.view, **context.to_dict())


@users_bp.route("/<int:entity_id>/edit", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="User", action="edit")
@login_required
def edit(context, entity_id):
    if request.method == "POST":
        try:
            u = user_service.get_by_id(entity_id)
            user_service.update(u, request.form.to_dict())
            flash("User updated.", "success")
            return redirect(url_for("users_bp.view", entity_id=u.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.edit, **context.to_dict())


@users_bp.route("/<int:entity_id>/delete", methods=["POST"])
@login_required
def delete(entity_id):
    try:
        user_service.delete(entity_id)
        flash("User deleted.", "success")
        return redirect(url_for("users_bp.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("users_bp.view", entity_id=entity_id))
