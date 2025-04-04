# app/routes/web/__init__.py

import logging
from flask import Blueprint
from app.routes.web.auth import login, logout
from app.routes.web.index import index_bp  # 👈 your blueprint with routes

logger = logging.getLogger(__name__)

# Create blueprints for web UI (these should be imported from their own modules ideally)
users_bp = Blueprint("users", __name__, url_prefix="/users")
companies_bp = Blueprint("companies", __name__, url_prefix="/companies")
contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")
opportunities_bp = Blueprint("opportunities", __name__, url_prefix="/opportunities")
relationships_bp = Blueprint("relationships", __name__, url_prefix="/relationships")
crisp_scores_bp = Blueprint("crisp_scores_bp", __name__, url_prefix="/crisp-scores")
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

# Register login/logout routes with auth blueprint
auth_bp.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
auth_bp.add_url_rule("/logout", view_func=logout, methods=["GET"])

def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.debug("Registering web blueprints...")

    app.register_blueprint(index_bp)         # 👈 now includes route for "/"
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(relationships_bp)
    app.register_blueprint(crisp_scores_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)

    logger.debug("Web blueprints registered successfully.")
