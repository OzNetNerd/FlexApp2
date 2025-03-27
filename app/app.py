import logging
from datetime import datetime
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session as flask_session,
    jsonify,
    make_response,
)
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from app.routes.web import register_web_blueprints
from app.routes.base.components.template_renderer import render_safely
from app.models.base import db
from app.models.user import User
from flask import current_app

logger = logging.getLogger(__name__)

# Global extensions
login_manager = LoginManager()
migrate = Migrate()


@login_manager.unauthorized_handler
def unauthorized():
    return make_response("🔒 Unauthorized - Please log in first", 401)


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_app(config_class=Config):
    configure_logging()

    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(config_class)

    # ✅ Secure session configuration using Flask's built-in session management
    app.config.update(
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24,  # 1 day
        SESSION_PERMANENT=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # Set to False for local dev if needed
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_DURATION=60 * 60 * 24 * 30,  # 30 days
        REMEMBER_COOKIE_HTTPONLY=True,
    )

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        with current_app.app_context():
            return db.session.get(User, int(user_id))

    @app.before_request
    def require_login():
        logger = logging.getLogger(__name__)
        whitelisted = [
            "auth_bp.login",
            "auth_bp.logout",
            "static",
            "debug_session",
        ]

        endpoint = request.endpoint
        if endpoint is None:
            return

        logger.debug(f"Before request: {endpoint}, Authenticated: {current_user.is_authenticated}")
        logger.debug(f"Session contents: {dict(flask_session) if flask_session else 'None'}")
        logger.debug(f"User ID: {current_user.get_id() if current_user.is_authenticated else None}")
        logger.debug(f"Cookies: {request.cookies}")

        if not current_user.is_authenticated:
            if endpoint in whitelisted or endpoint.startswith("static") or endpoint.startswith("api_") or endpoint.endswith(".data"):
                return
            return redirect(url_for("auth_bp.login", next=request.path))

    # ✅ Register all web routes
    register_web_blueprints(app)

    @app.route("/debug-session")
    def debug_session():
        result = {
            "is_authenticated": current_user.is_authenticated,
            "session_keys": list(flask_session.keys()) if flask_session else [],
            "permanent": flask_session.permanent if flask_session else None,
            "user_id": current_user.get_id() if current_user.is_authenticated else None,
            "remember_token": request.cookies.get("remember_token") is not None,
            "cookies": {k: v for k, v in request.cookies.items()},
        }
        return jsonify(result)

    with app.app_context():
        logger.debug("--- Registered URL Rules ---")
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.endpoint):
            logger.debug(f"Endpoint: {rule.endpoint}, Methods: {rule.methods}, Rule: {rule}")

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    @app.errorhandler(404)
    def page_not_found(e):
        context = {"error": e}
        return render_safely("errors/404.html", context, "Page not found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        context = {"error": e}
        return render_safely("errors/500.html", context, "Internal server error."), 500

    return app


# Run app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
