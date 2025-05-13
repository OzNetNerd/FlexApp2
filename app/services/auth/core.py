from app.services.service_base import ServiceBase


class AuthCoreService(ServiceBase):
    def __init__(self, model=None):
        super().__init__(model)

    @property
    def model_class(self):
        """Get the model class this service operates on."""
        return self._model_class

    @model_class.setter
    def model_class(self, value):
        """Set the model class this service operates on."""
        self._model_class = value

    def find_user_by_email(self, email):
        """Find a user by email."""
        self.logger.info(f"Looking up user with email: {email}")
        return self.model_class.query.filter_by(email=email).first()
