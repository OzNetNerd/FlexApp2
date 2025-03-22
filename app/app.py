from flask import Flask
from datetime import datetime
from config import Config
from routes import register_blueprints
from routes.base.components.template_renderer import render_safely
import os
import logging


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_app(config_class=Config):
    configure_logging()

    """Create and configure the Flask application."""
    app = Flask(__name__,
                static_folder='static',
                static_url_path='/static')
    app.config.from_object(config_class)

    # Set up logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log application configuration details
    logger.debug(f"Flask app initialized with debug={app.debug}")
    logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    logger.debug(f"Current working directory: {os.getcwd()}")

    # Delay import to avoid circular import
    from services import init_db
    init_db(app)

    # Register blueprints
    register_blueprints(app)

    # Debug: Log all registered URL rules
    with app.app_context():
        logger.debug("--- Registered URL Rules ---")
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.endpoint):
            logger.debug(f"Endpoint: {rule.endpoint}, Methods: {rule.methods}, Rule: {rule}")

    # Add template context processors
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Define error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        context = {'error': e}
        fallback_message = "Page not found. The requested URL was not found on the server."
        response = render_safely('errors/404.html', context, fallback_message)
        return response if isinstance(response, tuple) and len(response) > 1 else (response, 404)

    @app.errorhandler(500)
    def internal_server_error(e):
        context = {'error': e}
        fallback_message = "Internal server error. The server encountered an unexpected condition."
        response = render_safely('errors/500.html', context, fallback_message)
        return response if isinstance(response, tuple) and len(response) > 1 else (response, 500)

    return app


# Create the app
app = create_app()

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(debug=True)
