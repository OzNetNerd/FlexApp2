# app/routes/web/tasks.py
from app.models.pages.task import Task
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig


tasks_bp = create_crud_blueprint(BlueprintConfig(Task))
