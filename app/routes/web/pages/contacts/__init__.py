from flask import Blueprint
from app.models.pages.contact import Contact
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main contact blueprint
contacts_bp = create_crud_blueprint(BlueprintConfig(model_class=Contact))

# Import and register routes from submodules
from . import dashboard, filters, statistics, views

# Blueprint is already created and routes registered via decorators