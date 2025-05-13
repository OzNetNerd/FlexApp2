# app/routes/api/pages/companies/crud.py

from flask import jsonify, request
from app.models import Company
from app.services.crud_service import CRUDService
from app.routes.api.pages.companies import companies_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig

# Register CRUD service and config
company_service = CRUDService(Company)
company_api_crud_config = ApiCrudRouteConfig(blueprint=companies_api_bp, entity_table_name="Company", service=company_service)


# You can add additional CRUD-related endpoints here if needed
@companies_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all companies."""
    companies = company_service.get_all()
    return jsonify([company.to_dict() for company in companies])


@companies_api_bp.route("/<int:company_id>", methods=["GET"])
def get(company_id):
    """Get a company by ID."""
    company = company_service.get_by_id(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    return jsonify(company.to_dict())

@companies_api_bp.route("/<int:company_id>", methods=["PATCH"])
def update_company_field(company_id):
    """Update a single field of a company."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        logger.info(f"Updating company {company_id} with data: {data}")

        # Get current company to validate it exists
        company = company_service.get_by_id(company_id)
        if not company:
            return jsonify({"error": f"Company with ID {company_id} not found"}), 404

        # Update only provided fields
        updated_company = company_service.update(company, data)
        return jsonify(updated_company.to_dict())
    except Exception as e:
        logger.error(f"Error updating company {company_id}: {str(e)}")
        return jsonify({"error": f"Failed to update: {str(e)}"}), 500