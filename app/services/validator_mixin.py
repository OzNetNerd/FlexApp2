# app/services/validator_mixin.py


class ValidatorMixin:
    """
    Optional base class for adding validation to CRUD services.
    """

    def validate_create(self, data: dict) -> list[str]:
        return []

    def validate_update(self, item, data: dict) -> list[str]:
        return []
