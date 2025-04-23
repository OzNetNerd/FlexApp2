from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.task import Task
from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
task_service = CRUDService(Task)
templates = default_crud_templates("Task")


@tasks_bp.route("/", methods=["GET"])
@use_context(TableContext, entity_table_name="Task", action="index")
@login_required
def index(context):
    return render_template(templates.index, **context.to_dict())


@tasks_bp.route("/create", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Task", action="create")
@login_required
def create(context):
    if request.method == "POST":
        try:
            ent = task_service.create(request.form.to_dict())
            flash("Task created.", "success")
            return redirect(url_for("tasks_bp.view", entity_id=ent.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.create, **context.to_dict())


@tasks_bp.route("/<int:entity_id>", methods=["GET"])
@use_context(EntityContext, entity_table_name="Task", action="view")
@login_required
def view(context, entity_id):
    return render_template(templates.view, **context.to_dict())


@tasks_bp.route("/<int:entity_id>/edit", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Task", action="edit")
@login_required
def edit(context, entity_id):
    if request.method == "POST":
        try:
            t = task_service.get_by_id(entity_id)
            task_service.update(t, request.form.to_dict())
            flash("Task updated.", "success")
            return redirect(url_for("tasks_bp.view", entity_id=t.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.edit, **context.to_dict())


@tasks_bp.route("/<int:entity_id>/delete", methods=["POST"])
@login_required
def delete(entity_id):
    try:
        task_service.delete(entity_id)
        flash("Task deleted.", "success")
        return redirect(url_for("tasks_bp.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("tasks_bp.view", entity_id=entity_id))
