# app/routes/api/pages/opportunities/crud.py

from flask import jsonify, request
from app.models import Opportunity
from app.services.crud_service import CRUDService
from app.routes.api.pages.opportunities import opportunities_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig

# Register CRUD service and config
opportunity_service = CRUDService(Opportunity)
opportunity_api_crud_config = ApiCrudRouteConfig(
    blueprint=opportunities_api_bp, entity_table_name="Opportunity", service=opportunity_service
)


# You can add additional CRUD-related endpoints here if needed
@opportunities_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all opportunities."""
    opportunities = opportunity_service.get_all()
    return jsonify([opportunity.to_dict() for opportunity in opportunities])


@opportunities_api_bp.route("/<int:opportunity_id>", methods=["GET"])
def get(opportunity_id):
    """Get an opportunity by ID."""
    opportunity = opportunity_service.get_by_id(opportunity_id)
    if not opportunity:
        return jsonify({"error": "Opportunity not found"}), 404
    return jsonify(opportunity.to_dict())
