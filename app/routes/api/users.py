from app.models import User
from app.routes.api import api_users_bp
from app.routes.api.generic import GenericAPIRoutes
from app.services.user_service import UserService  # ✅
import logging

logger = logging.getLogger(__name__)

logger.debug("Instantiating GenericAPIRoutes for the User model.")
user_api_routes = GenericAPIRoutes(
    blueprint=api_users_bp,
    model=User,
    service=UserService(User),  # ✅
    api_prefix="/api/users",
    required_fields=["username", "email", "password"],
    unique_fields=["username", "email"],
)
logger.info("User API routes instantiated successfully.")
