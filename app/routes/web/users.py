# app/routes/web/users.py

from app.models import User
from app.routes.web import users_bp
from app.routes.web.generic_crud_routes import GenericWebRoutes

import logging
from app.routes.base.tabs.users import get_users_tabs


logger = logging.getLogger(__name__)

# Create a custom CRUD routes class for Users
class UserCRUDRoutes(GenericWebRoutes):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Set up CRUD routes for managing users within the 'users_bp' blueprint.
# This configures routes for creating, reading, updating, and deleting users.
# The setup includes:
# - The `User` model as the target for CRUD operations.
# - Required fields for user creation: `username`, `name`, and `email`.
# - A uniqueness constraint on the `username` field to prevent duplicate entries.
# - The template used for rendering the users table: `entity_tables/users.html`.
# - A custom function (`get_users_tabs`) to define the tabs displayed on the user creation page.
logger.debug("Setting up CRUD routes for User model.")
user_routes = UserCRUDRoutes(
    model=User,
    blueprint=users_bp,
    index_template="entity_tables/users.html",
    required_fields=["username", "name", "email"],
    unique_fields=["username"],
    # create_tabs_function=get_users_tabs,
)

logger.info("User CRUD routes setup successfully.")
