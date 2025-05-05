"""Email value object."""

import re


class Email:
    """
    Value object representing an email address.

    Validates email format and provides consistent access to email properties.

    Attributes:
        value: The validated email address string.
    """

    def __init__(self, value):
        """
        Initialize and validate an email address.

        Args:
            value: Email address string.

        Raises:
            ValueError: If email format is invalid.
        """
        if not value:
            raise ValueError("Email cannot be empty")

        # Simple validation
        if not self._is_valid_email(value):
            raise ValueError(f"Invalid email format: {value}")

        self._value = value.lower().strip()

    @staticmethod
    def _is_valid_email(email):
        """
        Validate email format using regex.

        Args:
            email: Email string to validate.

        Returns:
            bool: True if email format is valid.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @property
    def value(self):
        """Get the email value."""
        return self._value

    @property
    def domain(self):
        """Get the domain part of the email."""
        return self._value.split("@")[1]

    @property
    def username(self):
        """Get the username part of the email."""
        return self._value.split("@")[0]

    def __eq__(self, other):
        """Compare two email objects for equality."""
        if isinstance(other, Email):
            return self.value == other.value
        return False

    def __str__(self):
        """Return string representation of the email."""
        return self.value
