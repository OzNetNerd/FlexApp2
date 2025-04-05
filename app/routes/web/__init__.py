import logging

logger = logging.getLogger(__name__)


def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.debug("Registering web blueprints...")

    # Import blueprints here to avoid circular imports
    from app.routes.web.auth import auth_bp
    from app.routes.web.index import index_bp
    from app.routes.web.crud.companies import companies_bp
    from app.routes.web.crud.contacts import contacts_bp
    from app.routes.web.crud.opportunities import opportunities_bp
    from app.routes.web.crud.users import users_bp
    from app.routes.web.crud.tasks import tasks_bp
    from app.routes.web.settings import settings_bp
    from app.routes.web.relationships import relationships_bp
    from app.routes.web.crisp_score import crisp_scores_bp

    # Register all blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(relationships_bp)
    app.register_blueprint(crisp_scores_bp)

    logger.debug("Web blueprints registered successfully.")
