import logging
from flask import Blueprint, abort, render_template
from flask_login import current_user

from app.models.setting import Setting
from app.routes.web.crud.components.generic_crud_routes import GenericWebRoutes

logger = logging.getLogger(__name__)

# Define the blueprint for this module
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


class SettingsCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Setting model.
    """

    def _preprocess_form_data(self, form_data):
        return form_data

    def index(self):
        """Overrides the default index to inject 'setting' into context."""
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)

        setting = Setting.query.filter_by(key="debug").first()
        if not setting:
            setting = Setting(key="debug", value="false").save()

        logger.debug(f"Loaded setting: {setting}")

        return render_template(
            self.index_template,
            setting=setting,
            title="Settings",
        )


# Bind the CRUD routes to the settings blueprint
settings_routes = SettingsCRUDRoutes(
    blueprint=settings_bp,
    model=Setting,
    index_template="pages/misc/settings.html",
    required_fields=[],
    unique_fields=[],
)
