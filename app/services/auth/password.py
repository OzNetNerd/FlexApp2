from werkzeug.security import check_password_hash
from app.utils.app_logging import get_logger

logger = get_logger()

class PasswordService:
    def verify_password(self, user, password):
        """Verify a user's password."""
        if user and check_password_hash(user.password_hash, password):
            logger.info(f"Password valid for user: {user.email}")
            return True
        return False