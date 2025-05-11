from flask import Blueprint
from app.models.pages.company import Company
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main company blueprint
companies_bp = create_crud_blueprint(BlueprintConfig(model_class=Company))

# Import and register routes from submodules
from . import dashboard, filters, statistics

# Blueprint is already created and routes registered via decorators