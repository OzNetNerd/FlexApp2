# app/routes/web/tasks.py
from app.models.task import Task
from app.routes.web.blueprint_factory import create_crud_blueprint

tasks_bp = create_crud_blueprint(Task)