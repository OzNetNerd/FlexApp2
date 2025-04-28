# app/routes/api/relationships.py

from flask import Blueprint, request

from app.services.relationship_service import RelationshipService
from app.utils.app_logging import get_logger

from .json_utils import json_endpoint

logger = get_logger()

relationships_api_bp = Blueprint("relationships_api_bp", __name__, url_prefix="/api/relationships")


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


@relationships_api_bp.route("/create", methods=["POST"])
@json_endpoint
def create_relationship():
    """Create a relationship between entities"""
    data = request.json
    entity1_type = data.get("entity1_type")
    entity1_id = data.get("entity1_id")
    entity2_type = data.get("entity2_type")
    entity2_id = data.get("entity2_id")
    relationship_type = data.get("relationship_type", "Related")

    success, relationship, message = RelationshipService.create_relationship(
        entity1_type, entity1_id, entity2_type, entity2_id, relationship_type
    )

    return {"success": success, "message": message}