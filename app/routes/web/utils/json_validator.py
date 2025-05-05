# MIGRATED

import json
from typing import Any, Dict, List

from app.utils.app_logging import get_logger

logger = get_logger()


class JSONValidator:
    """Validates and ensures data is JSON serializable."""

    def validate_json_serializable(self, data: Dict[str, Any], path: str = "") -> List[str]:
        """
        Recursively validate that a dictionary is JSON serializable.

        Args:
            data: The dictionary to validate.
            path: The dot-path representing current traversal (for error reporting).

        Returns:
            List[str]: List of paths where serialization errors were found.
        """
        issues = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                try:
                    json.dumps({key: value})
                except TypeError as e:
                    logger.error(f"❌  JSON serialization error at {current_path}: {str(e)}")
                    issues.append(f"{current_path}: {type(value).__name__}")

                # Recursively check nested values
                if isinstance(value, dict):
                    issues.extend(self.validate_json_serializable(value, current_path))
                elif isinstance(value, list):
                    for i, entity in enumerate(value):
                        if isinstance(entity, dict):
                            issues.extend(self.validate_json_serializable(entity, f"{current_path}[{i}]"))

        return issues

    def ensure_json_serializable(self, data):
        """
        Recursively convert complex objects to JSON-safe formats.

        Args:
            data: Any object or structure to convert.

        Returns:
            A version of the input data that is JSON serializable.
        """
        if isinstance(data, dict):
            return {k: self.ensure_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.ensure_json_serializable(entity) for entity in data]
        elif hasattr(data, "__dict__"):
            return self.ensure_json_serializable(data.__dict__)
        return data
