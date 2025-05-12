from app.utils.app_logging import get_logger

logger = get_logger()


class AuthCoreService:
    def __init__(self, model):
        self.model = model

    def find_user_by_email(self, email):
        """Find a user by email."""
        logger.info(f"Looking up user with email: {email}")
        return self.model.query.filter_by(email=email).first()