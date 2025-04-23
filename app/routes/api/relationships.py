# app/routes/api/relationships.py

from flask import Blueprint
from app.services.relationship_service import RelationshipService
from app.utils.app_logging import get_logger
from .json_utils import json_endpoint

logger = get_logger()

relationships_api_bp = Blueprint(
    "relationships_api_bp", __name__, url_prefix="/api/relationships"
)

@relationships_api_bp.route("/user/<int:user_id>/companies", methods=["GET"])
@json_endpoint
def get_user_companies(user_id: int):
    return RelationshipService.get_user_companies(user_id)

@relationships_api_bp.route("/user/<int:user_id>/opportunities", methods=["GET"])
@json_endpoint
def get_user_opportunities(user_id: int):
    return RelationshipService.get_user_opportunities(user_id)

@relationships_api_bp.route("/user/<int:user_id>/contacts", methods=["GET"])
@json_endpoint
def get_user_contacts(user_id: int):
    return RelationshipService.get_user_contacts(user_id)

@relationships_api_bp.route("/contact/<int:contact_id>/contacts", methods=["GET"])
@json_endpoint
def get_contact_contacts(contact_id: int):
    return RelationshipService.get_contact_contacts(contact_id)

@relationships_api_bp.route("/contact/<int:contact_id>/opportunities", methods=["GET"])
@json_endpoint
def get_contact_opportunities(contact_id: int):
    return RelationshipService.get_contact_opportunities(contact_id)

@relationships_api_bp.route("/opportunity/<int:opportunity_id>/companies", methods=["GET"])
@json_endpoint
def get_opportunity_companies(opportunity_id: int):
    return RelationshipService.get_opportunity_companies(opportunity_id)
