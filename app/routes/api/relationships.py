# app/routes/api/relationships.py

from flask import Blueprint, request, abort
from app.services.relationship_service import RelationshipService
from app.utils.app_logging import get_logger

logger = get_logger()

# Blueprint for relationship mappings
relationships_api_bp = Blueprint(
    "relationships_api_bp", __name__, url_prefix="/api/relationships"
)

@relationships_api_bp.route("/user/<int:user_id>/companies", methods=["GET"])
def get_user_companies(user_id: int):
    """Return companies related to a given user."""
    data = RelationshipService.get_user_companies(user_id)
    return {"data": data}

@relationships_api_bp.route("/user/<int:user_id>/opportunities", methods=["GET"])
def get_user_opportunities(user_id: int):
    """Return opportunities related to a given user."""
    data = RelationshipService.get_user_opportunities(user_id)
    return {"data": data}

@relationships_api_bp.route("/user/<int:user_id>/contacts", methods=["GET"])
def get_user_contacts(user_id: int):
    """Return contacts related to a given user."""
    data = RelationshipService.get_user_contacts(user_id)
    return {"data": data}

@relationships_api_bp.route("/contact/<int:contact_id>/contacts", methods=["GET"])
def get_contact_contacts(contact_id: int):
    """Return contacts related to a given contact."""
    data = RelationshipService.get_contact_contacts(contact_id)
    return {"data": data}

@relationships_api_bp.route("/contact/<int:contact_id>/opportunities", methods=["GET"])
def get_contact_opportunities(contact_id: int):
    """Return opportunities related to a given contact."""
    data = RelationshipService.get_contact_opportunities(contact_id)
    return {"data": data}

@relationships_api_bp.route("/opportunity/<int:opportunity_id>/companies", methods=["GET"])
def get_opportunity_companies(opportunity_id: int):
    """Return companies related to a given opportunity."""
    data = RelationshipService.get_opportunity_companies(opportunity_id)
    return {"data": data}
