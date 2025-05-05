# src/infrastructure/context/base_context.py

from typing import Any, Dict, Optional

from src.infrastructure.logging import get_logger

logger = get_logger()


class BaseContext:
    """Base context class for all application contexts.

    This class provides common functionality for both API and web contexts,
    including attribute management, string representation, and conversion
    to dictionary format for serialization.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with common attributes for all contexts.

        Args:
            **kwargs: Arbitrary keyword arguments to be set as attributes
        """
        # Set all kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.debug(f"Set attribute '{key}' = {value}")

    def __repr__(self) -> str:
        """Create a detailed string representation of the context.

        Returns:
            str: A string containing the class name and all non-private attributes
        """
        attributes = ", ".join(f"{key}={repr(value)}" for key, value in vars(self).items() if not key.startswith("_"))
        return f"{self.__class__.__name__}({attributes})"

    def __str__(self) -> str:
        """Create a user-friendly string representation of the context.

        Returns:
            str: The class name and empty parentheses
        """
        return f"{self.__class__.__name__}()"

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for template rendering or serialization.

        Returns:
            Dict[str, Any]: Dictionary containing all non-private attributes
        """
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}
