from app.models import User, Note
from app.routes.web import users_bp
from app.routes.web.generic import GenericWebRoutes
import logging

logger = logging.getLogger(__name__)


# Create a custom CRUD routes class for Users
class UserCRUDRoutes(GenericWebRoutes):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_view_context(self, item, context):
        """Add notes_model to the view context."""
        logger.debug(f"Adding 'notes_model' to the view context for User {item.id}.")
        context["notes_model"] = Note


# Set up the CRUD routes for users
logger.debug("Setting up CRUD routes for User model.")
user_routes = UserCRUDRoutes(
    model=User,
    blueprint=users_bp,
    index_template="users.html",
    required_fields=["username", "name", "email"],
    unique_fields=["username"],
)

logger.info("User CRUD routes setup successfully.")
