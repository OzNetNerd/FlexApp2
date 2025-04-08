# Example 1: Full CRUD Entity
# app/routes/companies.py
import logging
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.contact import Contact

logger = logging.getLogger(__name__)

# Define the blueprint
contacts_bp = Blueprint("contacts_bp", __name__, url_prefix="/contacts")

# Create a service instance
contact_service = CRUDService(Contact)

# Register all standard CRUD routes
register_crud_routes(contacts_bp, "Contact", service=contact_service)
