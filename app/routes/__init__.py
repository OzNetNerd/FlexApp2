import logging

logger = logging.getLogger(__name__)


def register_blueprints(app):
    """Register all blueprints with the Flask application."""
    logger.info("Registering all application blueprints...")

    # Import registration functions directly here instead of importing modules
    from app.routes.web import register_web_blueprints

    # Register web blueprints
    register_web_blueprints(app)

    # Try-except for API blueprints to handle case where API module doesn't exist yet
    try:
        from app.routes.api import register_api_blueprints
        register_api_blueprints(app)
    except (ImportError, AttributeError) as e:
        logger.warning(f"API blueprints could not be registered: {e}")
        logger.warning("API routes will not be available")

    logger.info("Blueprint registration completed")