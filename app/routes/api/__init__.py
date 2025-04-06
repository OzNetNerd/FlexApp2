import logging
from app.routes.api.resources import GenericDataAPI
from app.models import User, Company, Contact, Opportunity  # Your models

logger = logging.getLogger(__name__)

# Initialize the Generic Data API
data_api = GenericDataAPI()

# Register resources
data_api.register_resource('users', User, search_fields=['username', 'name', 'email'])
data_api.register_resource('companies', Company, search_fields=['name'])
data_api.register_resource('opportunities', Opportunity, search_fields=['name', 'description'])
data_api.register_resource('contacts', Contact, search_fields=['name', 'email'])


def register_api_blueprints(app):
    """Register all API blueprints with the Flask application."""
    logger.info("Registering API blueprints...")

    # Import existing blueprints to avoid circular imports
    from app.routes.api.companies import companies_api_bp
    from app.routes.api.contacts import contacts_api_bp
    from app.routes.api.opportunities import opportunities_api_bp
    from app.routes.api.users import users_api_bp
    from app.routes.api.tasks import tasks_api_bp

    # Register existing blueprints
    app.register_blueprint(companies_api_bp)
    app.register_blueprint(contacts_api_bp)
    app.register_blueprint(opportunities_api_bp)
    app.register_blueprint(users_api_bp)
    app.register_blueprint(tasks_api_bp)

    # Register data API blueprints
    logger.info("Registering data API blueprints...")
    for resource_type, blueprint in data_api.resource_blueprints.items():
        app.register_blueprint(blueprint)
        logger.info(f"Registered data API blueprint for {resource_type}")

    logger.info("API blueprints registered successfully.")