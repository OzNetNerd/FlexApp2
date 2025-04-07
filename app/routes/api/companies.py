import logging
from flask import Blueprint, jsonify, request, url_for, redirect, flash
import requests
from app.models.company import Company
from app.services.crud_service import CRUDService
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext
logger = logging.getLogger(__name__)
TABLE_NAME = "Company"



logger = logging.getLogger(__name__)

TABLE_NAME = 'Company'

# Define the blueprint
companies_api_bp = Blueprint("api_companies", __name__, url_prefix="/api/companies")

company_service = CRUDService(Company)


@companies_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all companies."""
    companies = company_service.get_all()
    return jsonify([company.to_dict() for company in companies])


@companies_api_bp.route("/<int:item_id>", methods=["GET"])
def get_one(item_id):
    """Get a specific company."""
    company = company_service.get_by_id(item_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    return jsonify(company.to_dict())


@companies_api_bp.route("/", methods=["POST"])
def create():
    """Create a new company."""
    data = request.get_json()
    result = company_service.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201



@companies_api_bp.route("/<int:item_id>")
def view(item_id):
    """View company details via internal API call."""
    try:
        api_url = url_for("api_companies.get_one", item_id=item_id, _external=True)
        logger.info(f"[Company View] Fetching company from API: {api_url}")

        response = requests.get(api_url, timeout=5)
        logger.debug(f"[Company View] API response {response.status_code}: {response.text}")

        if response.status_code != 200:
            flash("Company not found or error in API response.", "danger")
            logger.warning(f"[Company View] Failed to fetch company {item_id}: {response.status_code}")
            return redirect(url_for("companies.list"))

        company_data = response.json()

    except requests.RequestException as e:
        logger.exception(f"[Company View] Request to API failed for company {item_id}")
        flash("Error fetching company details from API.", "danger")
        return redirect(url_for("companies.list"))

    context = SimpleContext(
        action="View",
        table_name=TABLE_NAME,
        item=company_data
    )
    return render_safely("pages/crud/view.html", context, "Failed to load company details.")


@companies_api_bp.route("/<int:item_id>", methods=["PUT"])
def update(item_id):
    """Update a company."""
    data = request.get_json()
    result = company_service.update(item_id, data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@companies_api_bp.route("/<int:item_id>", methods=["DELETE"])
def delete(item_id):
    """Delete a company."""
    result = company_service.delete(item_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


logger.info("Successfully set up 'Company' API routes.")