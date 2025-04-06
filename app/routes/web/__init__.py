import logging

logger = logging.getLogger(__name__)

def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.info("Registering web blueprints...")

    from app.routes.web.crud.companies import companies_bp
    from app.routes.web.crud.contacts import contacts_bp
    from app.routes.web.crud.opportunities import opportunities_bp
    from app.routes.web.crud.users import users_bp
    from app.routes.web.crud.tasks import tasks_bp
    # Uncomment when these are implemented
    # from app.routes.web.crud.search import search_bp
    # from app.routes.web.crud.generic import generic_bp
    # from app.routes.web.crud.router import misc_bp

    # Register all blueprints
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    # app.register_blueprint(misc_bp)
    # app.register_blueprint(search_bp)
    # app.register_blueprint(generic_bp)

    logger.info("Web blueprints registered successfully.")
