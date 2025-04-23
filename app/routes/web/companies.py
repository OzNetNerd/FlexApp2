# app/routes/web/companies.py

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.company import Company  # ← ADD THIS IMPORT
from app.routes.web.context import EntityContext, TableContext
from app.routes.web.context_utils import use_context
from app.routes.web.route_registration import default_crud_templates
# from app.services.crud_service import CRUDService
from app.services.crud_service import *
from app.utils.app_logging import get_logger

logger = get_logger()

companies_bp = Blueprint("companies_bp", __name__, url_prefix="/companies")
company_service = CRUDService(Company)
templates = default_crud_templates("Company")


@companies_bp.route("/", methods=["GET"])
@use_context(TableContext, entity_table_name="Company", action="index")
@login_required
def index(context):
    return render_template(templates.index, **context.to_dict())


@companies_bp.route("/create", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Company", action="create")
@login_required
def create(context):
    if request.method == "POST":
        try:
            entity = company_service.create(request.form.to_dict())
            flash("Company created.", "success")
            return redirect(url_for("companies_bp.view", entity_id=entity.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.create, **context.to_dict())


@companies_bp.route("/<int:entity_id>", methods=["GET"])
@use_context(EntityContext, entity_table_name="Company", action="view")
@login_required
def view(context, entity_id):
    return render_template(templates.view, **context.to_dict())


@companies_bp.route("/<int:entity_id>/edit", methods=["GET", "POST"])
@use_context(EntityContext, entity_table_name="Company", action="edit")
@login_required
def edit(context, entity_id):
    if request.method == "POST":
        try:
            cmp = company_service.get_by_id(entity_id)
            company_service.update(cmp, request.form.to_dict())
            flash("Company updated.", "success")
            return redirect(url_for("companies_bp.view", entity_id=cmp.id))
        except Exception as e:
            flash(str(e), "danger")
    return render_template(templates.edit, **context.to_dict())


@companies_bp.route("/<int:entity_id>/delete", methods=["POST"])
@login_required
def delete(entity_id):
    try:
        company_service.delete(entity_id)
        flash("Company deleted.", "success")
        return redirect(url_for("companies_bp.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("companies_bp.view", entity_id=entity_id))
