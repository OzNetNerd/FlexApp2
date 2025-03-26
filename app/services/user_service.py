from app.models import User
from app.services.crud_service import CRUDService
from app.services.validator_mixin import ValidatorMixin


class UserService(CRUDService, ValidatorMixin):
    """Custom service for User model with validation."""

    def validate_create(self, data):
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

    def validate_update(self, item, data):
        errors = []

        username = data.get("username")
        email = data.get("email")

        if username and username != item.username:
            if User.query.filter_by(username=username).first():
                errors.append("Username must be unique.")

        if email and email != item.email:
            if User.query.filter_by(email=email).first():
                errors.append("Email must be unique.")

        return errors
