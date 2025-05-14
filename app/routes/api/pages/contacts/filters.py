# app/routes/api/pages/contacts/filters.py

from flask import jsonify, request
from app.services.contact import ContactService
from app.routes.api.pages.contacts import contacts_api_bp

# Initialize specialized service
contact_service = ContactService()


@contacts_api_bp.route("/filtered", methods=["GET"])
def get_filtered_contacts():
    """Get contacts based on filter criteria."""
    filters = {
        "has_opportunities": request.args.get("has_opportunities"),
        "has_companies": request.args.get("has_companies"),
        "has_roles": request.args.get("has_roles"),
    }
    contacts = contact_service.get_filtered_entities(filters)

    # Convert SQLAlchemy objects to dict for JSON serialization
    result = [contact.to_dict() for contact in contacts]

    return jsonify(result)
