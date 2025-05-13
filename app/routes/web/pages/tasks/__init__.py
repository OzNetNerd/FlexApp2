# app/routes/web/pages/tasks/__init__.py
from flask import Blueprint
from app.models.pages.task import Task
from app.routes.web.utils.blueprint_factory import BlueprintConfig, create_crud_blueprint

# Create the main tasks blueprint
tasks_bp = create_crud_blueprint(BlueprintConfig(model_class=Task))

# Routes will be automatically discovered
