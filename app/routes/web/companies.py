import logging
from app.models import Company
from app.routes.web import companies_bp
from app.routes.web.generic_crud_routes import GenericWebRoutes

logger = logging.getLogger(__name__)

class CompanyCRUDRoutes(GenericWebRoutes):
    pass


# Set up CRUD routes for managing companies within the 'companies_bp' blueprint.
# This configures routes for creating, reading, updating, and deleting companies.
# The setup includes:
# - The `Company` model as the target for CRUD operations.
# - A required field for company creation: `name`.
# - A uniqueness constraint on the `name` field to prevent duplicate entries.
# - The template used for rendering the companies table: `entity_tables/companies.html`.
# - A custom function (`get_company_tabs`) to define the tabs displayed on the company creation page.
company_routes = CompanyCRUDRoutes(
    blueprint=companies_bp,
    model=Company,
    required_fields=["name"],
    unique_fields=["name"],
    index_template="entity_tables/companies.html",
    # create_tabs_function=get_company_tabs,
)

