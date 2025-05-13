# app/routes/api/pages/contacts/dashboard.py

from flask import jsonify, request
from app.services.contact import ContactService
from app.routes.api.pages.contacts import contacts_api_bp

# Initialize specialized service
contact_service = ContactService()


@contacts_api_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Get statistics for the contacts dashboard."""
    stats = contact_service.get_dashboard_stats()
    return jsonify(stats)


@contacts_api_bp.route("/dashboard/top", methods=["GET"])
def get_top_contacts():
    """Get top contacts by opportunity count."""
    limit = request.args.get("limit", 5, type=int)
    top_contacts = contact_service.get_top_contacts(limit)

    # Convert SQLAlchemy objects to dict for JSON serialization
    result = []
    for contact, count in top_contacts:
        contact_dict = contact.to_dict()
        contact_dict["opportunity_count"] = count
        result.append(contact_dict)

    return jsonify(result)


@contacts_api_bp.route("/dashboard/segments", methods=["GET"])
def get_engagement_segments():
    """Get contact segments by engagement level."""
    segments = contact_service.get_engagement_segments()
    return jsonify(segments)


@contacts_api_bp.route("/dashboard/growth", methods=["GET"])
def get_growth_data():
    """Get growth data for the chart."""
    months_back = request.args.get("months_back", 6, type=int)
    growth_data = contact_service.prepare_growth_data(months_back)
    return jsonify(growth_data)