# app/routes/api/pages/contacts/crud.py

from flask import jsonify, request
from app.models import Contact
from app.services.crud_service import CRUDService
from app.routes.api.pages.contacts import contacts_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig

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
