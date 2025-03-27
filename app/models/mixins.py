# app/models/mixins.py


class ValidatorMixin:
    """Mixin providing validation methods for create and update."""

    def validate_create(self, data: dict) -> list:
        """
        Override this method in your model to provide creation validation.

        Args:
            data (dict): Input data.

        Returns:
            list: Validation error messages.
        """
        return []

    def validate_update(self, data: dict) -> list:
        """
        Override this method in your model to provide update validation.

        Args:
            data (dict): Updated data.

        Returns:
            list: Validation error messages.
        """
        return []
