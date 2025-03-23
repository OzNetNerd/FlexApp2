import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class JSONValidator:
    """Validates and ensures JSON serializable data."""

    def validate_json_serializable(
        self, data: Dict[str, Any], path: str = ""
    ) -> List[str]:
        """
        Validate if a dictionary is fully JSON serializable and log any issues.
        Returns a list of problematic paths in the data structure.
        """
        issues = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                try:
                    # Test if this particular value is JSON serializable
                    json.dumps({key: value})
                except TypeError as e:
                    logger.error(
                        f"JSON serialization error at {current_path}: {str(e)}"
                    )
                    issues.append(f"{current_path}: {type(value).__name__}")

                # Recursively check nested dictionaries
                if isinstance(value, dict):
                    nested_issues = self.validate_json_serializable(value, current_path)
                    issues.extend(nested_issues)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            nested_issues = self.validate_json_serializable(
                                item, f"{current_path}[{i}]"
                            )
                            issues.extend(nested_issues)
        return issues

    def ensure_json_serializable(self, data):
        """Convert data to a JSON serializable format."""
        if isinstance(data, dict):
            return {k: self.ensure_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.ensure_json_serializable(item) for item in data]
        elif hasattr(data, "__dict__"):
            return self.ensure_json_serializable(data.__dict__)
        # Add other type conversions as needed
        return data
