# routes/web/contacts.py
from flask import Blueprint
from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.crud_service import CRUDService
from app.models.contact import Contact

from app.utils.app_logging import get_logger
logger = get_logger()

# Define the blueprint
contacts_bp = Blueprint("contacts_bp", __name__, url_prefix="/contacts")

# Create a service instance
contact_service = CRUDService(Contact)

# Define custom templates - FIXED VERSION
custom_templates = CrudTemplates(
    # Your custom template needs to be correctly capitalized to match the route_type
    # In the code, "view" is used as the route_type, not "View"
    create="pages/crud/create_view_edit_contact.html",
    view="pages/crud/create_view_edit_contact.html",
    edit="pages/crud/create_view_edit_contact.html",
    update="pages/crud/create_view_edit_contact.html",
)

# Add debug logging to verify templates are set correctly
logger.info(f"Custom templates: {custom_templates.to_dict()}")

# Register all standard CRUD routes with custom templates
contact_crud_config = CrudRouteConfig(
    blueprint=contacts_bp, entity_table_name="Contact", service=contact_service, templates=custom_templates
)
register_crud_routes(contact_crud_config)
