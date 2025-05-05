# user_service.py

from app.models import User
from app.services.crud_service import CRUDService
from app.services.validator_mixin import ValidatorMixin


class UserService(CRUDService, ValidatorMixin):
    """Service for User model operations with validation.

    This service handles business logic and data validation for User entities,
    providing a layer between GraphQL resolvers and the database model.
    """

    def validate_create(self, data):
        """Validate data for user creation."""
        errors = []
        required_fields = ["username", "email", "password"]

        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} is required.")

        if User.query.filter_by(username=data.get("username")).first():
            errors.append("Username must be unique.")
        if User.query.filter_by(email=data.get("email")).first():
            errors.append("Email must be unique.")

        return errors

    def validate_update(self, entity, data):
        """Validate data for user updates."""
        errors = []

        username = data.get("username")
        email = data.get("email")

        if username and username != entity.username:
            if User.query.filter_by(username=username).first():
                errors.append("Username must be unique.")

        if email and email != entity.email:
            if User.query.filter_by(email=email).first():
                errors.append("Email must be unique.")

        return errors

    def search_by_username(self, query):
        """Search users by username."""
        return User.search_by_username(query)
