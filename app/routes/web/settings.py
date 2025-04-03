import logging
from app.models.setting import Setting
from app.routes.web import settings_bp
from app.routes.web.generic import GenericWebRoutes

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
