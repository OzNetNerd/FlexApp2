# app/routes/api/pages/srs/categories.py

from flask import jsonify, request
from app.services.srs import SRSService
from app.routes.api.pages.srs import srs_api_bp

# Initialize service
srs_service = SRSService()


@srs_api_bp.route("/categories", methods=["POST"])
def create_category_api():
    """API endpoint to add a new category."""
    data = request.get_json() or {}
    name = data.get("name")
    color = data.get("color", "#0d6efd")
    icon = data.get("icon", "folder")

    if not name:
        return {"error": "Category name is required"}, 400

    category = srs_service.create_category(name, color, icon)

    return {"id": name, "name": name, "color": color, "icon": icon}, 201


@srs_api_bp.route("/categories", methods=["GET"])
def get_categories_api():
    """API endpoint to get all categories."""
    categories = srs_service.get_categories()
    return {"categories": categories}
