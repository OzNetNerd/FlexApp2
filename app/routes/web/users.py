from models import User, Note
from routes.web import users_bp
from routes.web.generic import GenericWebRoutes
import logging

logger = logging.getLogger(__name__)

# Create a custom CRUD routes class for Users
class UserCRUDRoutes(GenericWebRoutes):
    def add_view_context(self, item, context):
        """Add notes_model to the view context."""
        logger.debug(f"Adding 'notes_model' to the view context for User {item.id}.")
        context['notes_model'] = Note

# Set up the CRUD routes for users
logger.debug("Setting up CRUD routes for User model.")
user_routes = UserCRUDRoutes(
    blueprint=users_bp,
    model=User,
    index_template='users.html',
    required_fields=['username', 'name', 'email'],
    unique_fields=['username']
)

logger.info("User CRUD routes setup successfully.")
