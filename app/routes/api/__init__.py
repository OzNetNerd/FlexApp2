import logging

logger = logging.getLogger(__name__)


def register_api_blueprints(app, exclusions=None):
    """Register API blueprints excluding specified ones."""
    logger.info("Registering API blueprints with exclusions: %s", exclusions)

    if exclusions is None:
        exclusions = []

    from app.routes.api.companies import companies_api_bp
    from app.routes.api.contacts import contacts_api_bp
    from app.routes.api.opportunities import opportunities_api_bp
    from app.routes.api.users import users_api_bp
    from app.routes.api.tasks import tasks_api_bp

    # Only register blueprints that aren't in the exclusions list
    if "companies" not in exclusions:
        app.register_blueprint(companies_api_bp)
    if "contacts" not in exclusions:
        app.register_blueprint(contacts_api_bp)
    if "opportunities" not in exclusions:
        app.register_blueprint(opportunities_api_bp)
    if "users" not in exclusions:
        app.register_blueprint(users_api_bp)
    if "tasks" not in exclusions:
        app.register_blueprint(tasks_api_bp)

    # Register data API blueprints only if they don't conflict with explicit ones
    from app.routes.api.resources import GenericDataAPI

    # Initialize the Generic Data API
    data_api = GenericDataAPI()

    # Register only resources that don't have explicit blueprints
    for resource_type, blueprint in data_api.resource_blueprints.items():
        if resource_type not in ["companies", "contacts", "opportunities", "users", "tasks"] or resource_type in exclusions:
            app.register_blueprint(blueprint)
            logger.info(f"Registered data API blueprint for {resource_type}")

    logger.info("API blueprints registered successfully (with exclusions).")
