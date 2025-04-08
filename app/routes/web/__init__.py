# import logging
#
# logger = logging.getLogger(__name__)
#
# def register_web_blueprints_with_exclusions(app, exclusions=None):
#     """Register web blueprints excluding specified ones."""
#     logger.info("Registering web blueprints with exclusions: %s", exclusions)
#
#     if exclusions is None:
#         exclusions = []
#
#     # from app.routes.web.crud.companies import companies_bp
#     from app.routes.web.crud.contacts import contacts_bp
#     from app.routes.web.crud.opportunities import opportunities_bp
#     from app.routes.web.crud.users import users_bp
#     from app.routes.web.crud.tasks import tasks_bp
#     from app.routes.web.auth import auth_bp
#
#     # Only register blueprints that aren't in the exclusions list
#     # if 'companies' not in exclusions:
#     #     app.register_blueprint(companies_bp)
#     if 'contacts' not in exclusions:
#         app.register_blueprint(contacts_bp)
#     if 'opportunities' not in exclusions:
#         app.register_blueprint(opportunities_bp)
#     if 'users' not in exclusions:
#         app.register_blueprint(users_bp)
#     if 'tasks' not in exclusions:
#         app.register_blueprint(tasks_bp)
#     if 'auth' not in exclusions:
#         app.register_blueprint(auth_bp)
#     if 'settings' not in exclusions:
#         # Conditionally create and register settings_bp
#         from app.routes.blueprint_factory import create_blueprint
#         settings_bp = create_blueprint("settings_bp")
#         app.register_blueprint(settings_bp)
#     if 'relationships' not in exclusions:
#         # Conditionally create and register relationships_bp
#         from app.routes.blueprint_factory import create_blueprint
#         relationships_bp = create_blueprint("relationships_bp")
#         app.register_blueprint(relationships_bp)
#     if 'crisp_scores' not in exclusions:
#         # Conditionally create and register crisp_scores_bp
#         from app.routes.blueprint_factory import create_blueprint
#         crisp_scores_bp = create_blueprint("crisp_scores_bp")
#         app.register_blueprint(crisp_scores_bp)
#
#     logger.info("Web blueprints registered successfully (with exclusions).")