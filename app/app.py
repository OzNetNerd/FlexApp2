from datetime import datetime
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    make_response,
)
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from app.models.base import db
from app.models import User, Setting
from app.routes.api_router import register_api_routes
from app.routes.web_router import register_application_blueprints
from app.utils.app_logging import configure_logging
from app.routes.base.components.template_renderer import handle_template_error

# ---------------------------------------------
# Flask Extensions
# ---------------------------------------------
login_manager = LoginManager()
migrate = Migrate()


@login_manager.unauthorized_handler
def unauthorized():
    return make_response("🔒 Unauthorized - Please log in first", 401)


# ---------------------------------------------
# App Factory
# ---------------------------------------------
def create_app(config_class=Config):
    custom_logger = configure_logging()

    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(config_class)

    app.config.update(
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24,  # 1 day
        SESSION_PERMANENT=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_DURATION=60 * 60 * 24 * 30,  # 30 days
        REMEMBER_COOKIE_HTTPONLY=True,
    )

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Set the login view—check that the blueprint's name matches!
    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Register TypeError handler
    @app.errorhandler(TypeError)
    def handle_type_error(e):
        return handle_template_error(e, request.endpoint, request.path, "An error occurred while preparing the page context")

    @login_manager.user_loader
    def load_user(user_id):
        custom_logger.info(f"Loading user with ID: {user_id}")
        return db.session.get(User, int(user_id))

    # ----------------------------
    # Blueprint and route registration
    # ----------------------------
    register_api_routes(app)
    register_application_blueprints(app)

    # ---------------------------------------------
    # Attach logger to app
    # ---------------------------------------------
    app.logger = custom_logger
    app.custom_logger = custom_logger

    # ---------------------------------------------
    # Global before_request logging
    # ---------------------------------------------
    @app.before_request
    def log_request():
        custom_logger.info(f"Web Request {request.method} {request.path} from {request.remote_addr}")

    # ---------------------------------------------
    # Global before_request for login requirement
    # (This callback now comes *after* routes are registered)
    # ---------------------------------------------
    @app.before_request
    def require_login():
        whitelisted = [
            "auth_bp.login",
            "auth_bp.logout",
            "static",
            "debug_session",
        ]
        endpoint = request.endpoint
        custom_logger.info(f"require_login: endpoint = {endpoint}, user authenticated = {current_user.is_authenticated}")
        if endpoint is None:
            custom_logger.info("No endpoint found; skipping login check.")
            return
        if not current_user.is_authenticated:
            if endpoint in whitelisted or endpoint.startswith("static") or endpoint.startswith("api_") or endpoint.endswith(".data"):
                custom_logger.info(f"Access allowed for endpoint: {endpoint}")
                return
            custom_logger.info(f"Access denied for endpoint: {endpoint}; redirecting to login with next={request.path}")
            return redirect(url_for("auth_bp.login", next=request.path))

    # ---------------------------------------------
    # Global context injection
    # ---------------------------------------------
    @app.context_processor
    def inject_globals():
        return {"now": datetime.utcnow(), "logger": app.custom_logger}

    with app.app_context():
        from app import models

        custom_logger.info("Seeding settings and creating database tables.")
        Setting.seed()
        db.create_all()

    return app


# ---------------------------------------------
# Entrypoint
# ---------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
