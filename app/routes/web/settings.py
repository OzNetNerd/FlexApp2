import logging
from app.models.setting import Setting
from app.routes.web import settings_bp
from app.routes.web.generic_crud_routes import GenericWebRoutes

logger = logging.getLogger(__name__)


class SettingsCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Setting model.
    """

    def _preprocess_form_data(self, form_data):
        # You can customize this later if needed
        return form_data


# Define CRUD routes for the Setting model
# settings_routes = SettingsCRUDRoutes(
#     blueprint=settings_bp,
#     model=Setting,
#     index_template="settings.html",
#     required_fields=["key"],
#     unique_fields=["key"],
# )

settings_routes = SettingsCRUDRoutes(
    blueprint=settings_bp,
    model=Setting,
    index_template="settings.html",
    required_fields=[],
    unique_fields=[],
    # create_tabs_function=get_opportunity_tabs,
)


# need to inject 'context' in
# def index():
#     # Get the first/only setting row
#     setting = Setting.query.first()
#
#     # Fallback if it doesn't exist (optional)
#     if not setting:
#         setting = Setting(debug_enabled=False)
#         # optionally save it to DB
#
#     # Inject into context via 'extra'
#     ctx = Context(
#         title="Settings",
#         extra={"setting": setting}
#     )