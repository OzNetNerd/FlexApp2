# In app/routes/web/contacts.py
from flask import Blueprint
from app.models import Contact
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig

# Create a configuration object
config = BlueprintConfig(model_class=Contact)
contacts_bp = create_crud_blueprint(config)