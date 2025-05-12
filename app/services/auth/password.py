from werkzeug.security import check_password_hash
from app.services.service_base import ServiceBase

class PasswordService(ServiceBase):
    def verify_password(self, user, password):
        """Verify a user's password."""
        if user and check_password_hash(user.password_hash, password):
            self.logger.info(f"Password valid for user: {user.email}")
            return True
        return False