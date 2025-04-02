# app/routes/web/users.py

from app.models import User
from app.routes.web import users_bp
from app.routes.web.generic import GenericWebRoutes
import logging
from routes.base.ui.users import get_users_tabs


logger = logging.getLogger(__name__)

# Create a custom CRUD routes class for Users
class UserCRUDRoutes(GenericWebRoutes):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Set up the CRUD routes for users
logger.debug("Setting up CRUD routes for User model.")
user_routes = UserCRUDRoutes(
    model=User,
    blueprint=users_bp,
    index_template="entity_tables/users.html",
    required_fields=["username", "name", "email"],
    unique_fields=["username"],
    create_tabs_function=get_users_tabs,
)

logger.info("User CRUD routes setup successfully.")
