import logging
from flask import jsonify, request
from app.routes.blueprint_factory import create_blueprint
from app.models import Contact
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for contacts
contacts_api_bp = create_blueprint("api_contacts", url_prefix="/api/contacts")
contact_service = CRUDService(Contact)

@contacts_api_bp.route("/", methods=["GET"])
def get_all_contacts():
    """Get all contacts."""
    contacts = contact_service.get_all()
    return jsonify([contact.to_dict() for contact in contacts])

@contacts_api_bp.route("/<int:item_id>", methods=["GET"])
def get_contact(item_id):
    """Get a specific contact."""
    contact = contact_service.get_by_id(item_id)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404
    return jsonify(contact.to_dict())

@contacts_api_bp.route("/", methods=["POST"])
def create_contact():
    """Create a new contact."""
    data = request.get_json()
    # Validate required fields
    for field in ["first_name", "last_name", "email"]:
        if field not in data:
            return jsonify({"error": f"{field} is required."}), 400
    result = contact_service.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

@contacts_api_bp.route("/<int:item_id>", methods=["PUT"])
def update_contact(item_id):
    """Update a contact."""
    data = request.get_json()
    result = contact_service.update(item_id, data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@contacts_api_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_contact(item_id):
    """Delete a contact."""
    result = contact_service.delete(item_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

logger.info("Contact API routes instantiated successfully.")
