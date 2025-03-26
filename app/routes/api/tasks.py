from app.models import Task
from app.routes.api import api_tasks_bp
from app.routes.api.generic import GenericAPIRoutes
from app.services.crud_service import CRUDService
import logging

logger = logging.getLogger(__name__)

logger.debug("Instantiating GenericAPIRoutes for the Task model.")
task_api_routes = GenericAPIRoutes(
    blueprint=api_tasks_bp,
    model=Task,
    service=CRUDService(Task),
    api_prefix="/api/tasks",
    required_fields=["title", "status"],
    unique_fields=[],
)
logger.info("Task API routes instantiated successfully.")
