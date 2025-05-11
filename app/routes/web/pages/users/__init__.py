from flask import Blueprint
from app.models.pages.user import User
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the blueprint
users_bp = create_crud_blueprint(BlueprintConfig(model_class=User))

# Routes will be automatically discovered