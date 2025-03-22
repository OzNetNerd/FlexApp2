import os
import logging
from datetime import datetime
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from routes import register_blueprints
from routes.base.components.template_renderer import render_safely

from app.models.base import db  # ✅ db = SQLAlchemy() only, no app here

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

    app = Flask(
        __name__,
        static_folder='static',
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth_bp.login'

    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
        fallback = "Page not found. The requested URL was not found on the server."
        response = render_safely('errors/404.html', context, fallback)
        return response if isinstance(response, tuple) and len(response) > 1 else (response, 404)

    @app.errorhandler(500)
    def internal_server_error(e):
        context = {'error': e}
        fallback = "Internal server error. The server encountered an unexpected condition."
        response = render_safely('errors/500.html', context, fallback)
        return response if isinstance(response, tuple) and len(response) > 1 else (response, 500)

    return app


# Create app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
