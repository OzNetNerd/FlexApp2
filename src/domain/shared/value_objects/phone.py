"""Phone value object."""

import re


class Phone:
    """
    Value object representing a phone number.

    Validates phone format and provides consistent access to phone properties.

    Attributes:
        value: The validated phone number string.
    """

    def __init__(self, value):
        """
        Initialize and validate a phone number.

        Args:
            value: Phone number string.

        Raises:
            ValueError: If phone format is invalid.
        """
        if not value:
            self._value = None
            return

        # Remove non-numeric characters except + for international prefix
        cleaned = self._clean_phone_number(value)

        # Simple validation (allow empty phone)
        if cleaned and not self._is_valid_phone(cleaned):
            raise ValueError(f"Invalid phone format: {value}")

        self._value = cleaned

    @staticmethod
    def _clean_phone_number(phone):
        """
        Remove non-numeric characters except + for international prefix.

        Args:
            phone: Phone string to clean.

        Returns:
            str: Cleaned phone number.
        """
        if not phone:
            return None
        # Keep only digits, +, and spaces
        return re.sub(r'[^\d+\s]', '', phone)

    @staticmethod
    def _is_valid_phone(phone):
        """
        Validate phone format.

        Args:
            phone: Phone string to validate.

        Returns:
            bool: True if phone format is valid.
        """
        # Very basic validation - at least 7 digits
        digits = re.sub(r'[^\d]', '', phone)
        return len(digits) >= 7

    @property
    def value(self):
        """Get the phone value."""
        return self._value

    def __eq__(self, other):
        """Compare two phone objects for equality."""
        if isinstance(other, Phone):
            return self.value == other.value
        return False

    def __str__(self):
        """Return string representation of the phone."""
        return self.value if self.value else ""