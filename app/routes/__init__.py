import logging

logger = logging.getLogger(__name__)


def register_blueprints(app):
    """Register all blueprints with the Flask application."""
    logger.info("Registering all application blueprints...")

    # Import here to avoid circular imports
    from app.routes.web import register_web_blueprints
    from app.routes.api import register_api_blueprints

    # Register web blueprints
    register_web_blueprints(app)

    # Register API blueprints
    register_api_blueprints(app)

    logger.info("All blueprints registered successfully.")
