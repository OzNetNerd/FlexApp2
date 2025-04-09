# Example 1: Full CRUD Entity
# app/routes/companies.py
import logging
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.company import Company
from app.routes.base.web_utils import CrudRouteConfig

logger = logging.getLogger(__name__)

# Define the blueprint
companies_bp = Blueprint("companies_bp", __name__, url_prefix="/companies")

# Create a service instance
company_service = CRUDService(Company)

# Register all standard CRUD routes
company_crud_config = CrudRouteConfig(blueprint=companies_bp, entity_name="Company", service=company_service)
register_crud_routes(company_crud_config)

#
# # Example 2: Index-only Entity
# # app/routes/dashboard.py
# import logging
# from flask import Blueprint
# from app.routes.base.web_utils import register_crud_routes
#
# logger = logging.getLogger(__name__)
#
# # Define the blueprint
# dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/dashboard")
#
# # Register only the index route
# register_crud_routes(dashboard_bp, "Dashboard", routes=['index'])
#
#
# # Example 3: Entity with selective routes and a custom route
# # app/routes/tasks.py
# import logging
# from flask import Blueprint
# from app.routes.base.route_utils import register_routes
# from app.routes.base.components.template_renderer import render_safely
# from app.routes.base.components.entity_handler import SimpleContext
# from app.services.crud_service import CRUDService
# from app.models.task import Task
#
# logger = logging.getLogger(__name__)
#
# # Define the blueprint
# tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
#
# # Create a service instance
# task_service = CRUDService(Task)
#
# # Register only specific routes
# register_routes(tasks_bp, "Task",
#                 routes=['index', 'create', 'view'],
#                 service=task_service)
#
# # Register a custom route for 'edit' with a special template
# from app.routes.base.route_utils import register_route
# register_route(tasks_bp, 'edit', "Task",
#               template_override="pages/tasks/custom_edit.html")
#
# # Add another custom route
# @tasks_bp.route("/overdue")
# def overdue_tasks():
#     """Show overdue tasks."""
#     context = SimpleContext(title="Overdue Tasks", table_name="Task")
#     return render_safely("pages/tasks/overdue.html", context, "Failed to load overdue tasks.")
#
#
# # Example 4: Register individual routes manually for complete control
# # app/routes/users.py
# import logging
# from flask import Blueprint
# from app.routes.base.route_utils import register_route
# from app.services.crud_service import CRUDService
# from app.models.user import User
#
# logger = logging.getLogger(__name__)
#
# # Define the blueprint
# users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
#
# # Create a service instance
# user_service = CRUDService(User)

# # Register routes individually for maximum flexibility
# register_route(users_bp, 'index', "User")
# register_route(users_bp, 'create', "User", template_override="pages/users/custom_create.html")
# register_route(users_bp, 'view', "User", service=user_service)
# register_route(users_bp, 'edit', "User")
#
# # Custom route with completely custom implementation
# @users_bp.route("/dashboard")
# def dashboard():
#     """User dashboard with statistics."""
#     context = SimpleContext(title="User Dashboard", table_name="User")
#     return render_safely("pages/users/dashboard.html", context, "Failed to load user dashboard.")
