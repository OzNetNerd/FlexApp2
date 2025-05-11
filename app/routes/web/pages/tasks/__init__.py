# app/routes/web/pages/tasks/__init__.py
from flask import Blueprint
from app.models.pages.task import Task  # Change from User to Task
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main tasks blueprint
tasks_bp = create_crud_blueprint(BlueprintConfig(model_class=Task))  # Change to tasks_bp

# Import and register routes from submodules
from . import dashboard, filters, statistics