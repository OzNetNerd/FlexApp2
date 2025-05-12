from app.services.service_base import ServiceBase


class AuthCoreService(ServiceBase):
    def __init__(self, model=None):
        super().__init__(model)

    def find_user_by_email(self, email):
        """Find a user by email."""
        self.logger.info(f"Looking up user with email: {email}")
        return self.model_class.query.filter_by(email=email).first()