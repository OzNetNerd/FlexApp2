import logging
from flask import Blueprint, jsonify, request
from app.models.company import Company
from app.services.crud_service import CRUDService

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


logger.info("Company API routes setup successfully.")