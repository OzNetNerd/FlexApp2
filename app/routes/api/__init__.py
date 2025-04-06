import logging

logger = logging.getLogger(__name__)


def register_api_blueprints(app):
    """Register all API blueprints with the Flask application."""
    logger.info("Registering API blueprints...")

    # Import blueprints here to avoid circular imports
    from app.routes.api.companies import companies_api_bp
    from app.routes.api.contacts import contacts_api_bp
    from app.routes.api.opportunities import opportunities_api_bp
    from app.routes.api.users import users_api_bp
    from app.routes.api.tasks import tasks_api_bp
    # from app.routes.api.search import search_api_bp
    # from app.routes.api.generic import generic_api_bp

    # Register all blueprints
    app.register_blueprint(companies_api_bp)
    app.register_blueprint(contacts_api_bp)
    app.register_blueprint(opportunities_api_bp)
    app.register_blueprint(users_api_bp)
    app.register_blueprint(tasks_api_bp)
    # app.register_blueprint(search_api_bp)
    # app.register_blueprint(generic_api_bp)

    logger.info("API blueprints registered successfully.")