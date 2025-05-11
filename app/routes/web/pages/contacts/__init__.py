# app/routes/web/pages/contacts/__init__.py
from flask import Blueprint
from app.models.pages.contact import Contact
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main contact blueprint
contacts_bp = create_crud_blueprint(BlueprintConfig(model_class=Contact))