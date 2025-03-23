from dataclasses import dataclass, field
from typing import List, Dict, Any, Type
from flask import Blueprint
import logging

from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)


@dataclass
class CRUDRoutesBase:
    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    service: CRUDService = field(init=False)

    def __post_init__(self):
        logger.debug(f"Initializing CRUD routes base for {self.model.__name__}")
        self.service = CRUDService(self.model)  # Now we can pass model_class

    def _ensure_json_serializable(self, obj):
        """Ensure an object is JSON serializable by converting problematic types."""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif hasattr(obj, "__dict__"):
            return {
                k: self._ensure_json_serializable(v)
                for k, v in obj.__dict__.items()
                if not k.startswith("_") and not callable(v)
            }
        elif isinstance(obj, dict):
            return {k: self._ensure_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._ensure_json_serializable(item) for item in obj]
        else:
            logger.warning(
                f"Converting {type(obj).__name__} to string for JSON serialization"
            )
            return str(obj)

    def _validate_create(self, form_data):
        """Validate form data for creating a new item."""
        logger.debug(f"Validating create data for {self.model.__name__}")
        errors = []

        # Check required fields
        for field in self.required_fields:
            if field not in form_data or not form_data[field]:
                logger.warning(f"Required field '{field}' is missing or empty")
                errors.append(f"{field} is required.")

        # Check unique fields
        for field in self.unique_fields:
            if field in form_data and form_data[field]:
                existing = self.model.query.filter(
                    getattr(self.model, field) == form_data[field]
                ).first()
                if existing:
                    logger.warning(
                        f"Unique field '{field}' with value '{form_data[field]}' already exists"
                    )
                    errors.append(
                        f"{field} must be unique. '{form_data[field]}' is already in use."
                    )

        return errors

    def _validate_edit(self, item, form_data):
        """Validate form data for editing an existing item."""
        logger.debug(
            f"Validating edit data for {self.model.__name__} with id {item.id}"
        )
        errors = []

        # Check required fields
        for field in self.required_fields:
            if field not in form_data or not form_data[field]:
                logger.warning(f"Required field '{field}' is missing or empty")
                errors.append(f"{field} is required.")

        # Check unique fields, excluding the current item
        for field in self.unique_fields:
            if field in form_data and form_data[field]:
                # Skip if the value hasn't changed
                if getattr(item, field) == form_data[field]:
                    continue

                existing = self.model.query.filter(
                    getattr(self.model, field) == form_data[field]
                ).first()
                if existing and existing.id != item.id:
                    logger.warning(
                        f"Unique field '{field}' with value '{form_data[field]}' already exists"
                    )
                    errors.append(
                        f"{field} must be unique. '{form_data[field]}' is already in use."
                    )

        return errors

    def _validate_json_serializable(
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
                    import json

                    json.dumps({key: value})
                except TypeError as e:
                    logger.error(
                        f"JSON serialization error at {current_path}: {str(e)}"
                    )
                    issues.append(f"{current_path}: {type(value).__name__}")

                # Recursively check nested dictionaries
                if isinstance(value, dict):
                    nested_issues = self._validate_json_serializable(
                        value, current_path
                    )
                    issues.extend(nested_issues)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            nested_issues = self._validate_json_serializable(
                                item, f"{current_path}[{i}]"
                            )
                            issues.extend(nested_issues)
        return issues
