import os
import logging
from datetime import datetime
from flask import Flask, request, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from routes import register_blueprints
from routes.base.components.template_renderer import render_safely
from app.models.base import db
from app.models.user import User  # Required for user_loader

# Global extensions
login_manager = LoginManager()
migrate = Migrate()


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_app(config_class=Config):
    configure_logging()

    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth_bp.login'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Redirect all unauthenticated users unless whitelisted
    @app.before_request
    def require_login():
        whitelisted = [
            'auth_bp.login',
            'auth_bp.logout',
            'static',  # Allow static files
        ]
        if not current_user.is_authenticated and request.endpoint not in whitelisted:
            return redirect(url_for('auth_bp.login', next=request.path))

    # Setup logger
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.debug(f"Flask app initialized with debug={app.debug}")
    logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    logger.debug(f"Current working directory: {os.getcwd()}")

    # Avoid circular imports
    from services import init_db
    init_db(app)

    # Register blueprints
    register_blueprints(app)

    # Log registered routes
    with app.app_context():
        logger.debug("--- Registered URL Rules ---")
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.endpoint):
            logger.debug(f"Endpoint: {rule.endpoint}, Methods: {rule.methods}, Rule: {rule}")

    # Template context processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        context = {'error': e}
        return render_safely('errors/404.html', context, "Page not found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        context = {'error': e}
        return render_safely('errors/500.html', context, "Internal server error."), 500

    return app


# Create app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
