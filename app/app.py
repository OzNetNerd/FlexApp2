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
from app.routes.base.components.entity_handler import Context, ResourceContext
from flask import current_app

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger = logging.getLogger(__name__)
login_manager = LoginManager()
migrate = Migrate()

@login_manager.unauthorized_handler
def unauthorized():
    return make_response("🔒 Unauthorized - Please log in first", 401)

def create_app(config_class=Config):
    configure_logging()

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

    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        with current_app.app_context():
            return db.session.get(User, int(user_id))

    @app.before_request
    def require_login():
        whitelisted = [
            "auth_bp.login",
            "auth_bp.logout",
            "static",
            "debug_session",
        ]
        endpoint = request.endpoint
        if endpoint is None:
            return
        if not current_user.is_authenticated:
            if endpoint in whitelisted or endpoint.startswith("static") or endpoint.startswith("api_") or endpoint.endswith(".data"):
                return
            return redirect(url_for("auth_bp.login", next=request.path))

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

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    @app.errorhandler(404)
    def page_not_found(e):
        context = Context(
            title="404 Not Found",
            item=str(e),
            read_only=True
        )
        return render_safely("base/errors/404.html", context, "Page not found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        context = Context(
            title="500 Internal Server Error",
            item=str(e),
            read_only=True
        )
        return render_safely("base/errors/500.html", context, "Internal server error."), 500

    # ✅ Create all tables and seed demo data if necessary
    with app.app_context():
        from app import models
        db.create_all()

        # logger.debug("--- Registered URL Rules ---")
        # for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.endpoint):
            # logger.debug(f"Endpoint: {rule.endpoint}, Methods: {rule.methods}, Rule: {rule}")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
