# app/routes/api/pages/contacts/statistics.py

from flask import jsonify
from app.services.contact import ContactService
from app.routes.api.pages.contacts import contacts_api_bp

# Initialize specialized service
contact_service = ContactService()

@contacts_api_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """Get comprehensive statistics for the statistics page."""
    stats = contact_service.get_statistics()
    return jsonify(stats)