from models import User
from routes.api import api_users_bp
from routes.api.generic import GenericAPIRoutes
from services.crud_service import CRUDService
import logging

logger = logging.getLogger(__name__)

# API routes
user_service = CRUDService()
logger.debug("Instantiating GenericAPIRoutes for the User model.")
user_api_routes = GenericAPIRoutes(
   blueprint=api_users_bp,
   model=User,
   service=user_service,
   api_prefix='/api/users',
   required_fields=['username', 'email', 'password'],
   unique_fields=['username', 'email']
)
logger.info("User API routes instantiated successfully.")