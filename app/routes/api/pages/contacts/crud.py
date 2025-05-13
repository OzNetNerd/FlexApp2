# app/routes/api/pages/contacts/crud.py

from flask import jsonify, request
from app.models import Contact
from app.services.crud_service import CRUDService
from app.routes.api.pages.contacts import contacts_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig

from app.utils.app_logging import get_logger

logger = get_logger()

# Register CRUD service and config
contact_service = CRUDService(Contact)
contact_api_crud_config = ApiCrudRouteConfig(blueprint=contacts_api_bp, entity_table_name="Contact", service=contact_service)


# You can add additional CRUD-related endpoints here if needed
@contacts_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all contacts."""
    contacts = contact_service.get_all()
    return jsonify([contact.to_dict() for contact in contacts])


@contacts_api_bp.route("/<int:contact_id>", methods=["GET"])
def get(contact_id):
    """Get a contact by ID."""
    contact = contact_service.get_by_id(contact_id)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404
    return jsonify(contact.to_dict())

@contacts_api_bp.route("/<int:contact_id>", methods=["PATCH"])
def update_contact_field(contact_id):
    """Update a single field of a contact."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        logger.info(f"Updating contact {contact_id} with data: {data}")

        # Get current contact to validate it exists
        contact = contact_service.get_by_id(contact_id)
        if not contact:
            return jsonify({"error": f"Contact with ID {contact_id} not found"}), 404

        # Update only provided fields
        updated_contact = contact_service.update(contact, data)
        return jsonify(updated_contact.to_dict())
    except Exception as e:
        logger.error(f"Error updating contact {contact_id}: {str(e)}")
        return jsonify({"error": f"Failed to update: {str(e)}"}), 500