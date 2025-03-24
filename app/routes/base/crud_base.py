from dataclasses import dataclass, field
from typing import List, Dict, Any, Type
from flask import Blueprint
import logging
import json
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)


@dataclass
class CRUDRoutesBase:
    """
    Base class for CRUD route handlers.

    Attributes:
        model (Type): SQLAlchemy model class.
        blueprint (Blueprint): Flask blueprint to register routes to.
        required_fields (List[str]): Fields required for creation.
        unique_fields (List[str]): Fields that must be unique.
        service (CRUDService): CRUD service instance for data access.
    """

    model: Type
    blueprint: Blueprint
    required_fields: List[str] = field(default_factory=list)
    unique_fields: List[str] = field(default_factory=list)
    service: CRUDService = field(init=False)

    def __post_init__(self):
        """Initialize the service with the model."""
        logger.debug(f"Initializing CRUD routes base for {self.model.__name__}")
        self.service = CRUDService(self.model)

    def _preprocess_form_data(self, request_obj):
        """Optional hook for subclasses. Returns raw form by default."""
        return request_obj.form.to_dict()

    def _ensure_json_serializable(self, obj: Any) -> Any:
        """
        Recursively ensure that a value is JSON serializable.

        Args:
            obj (Any): The object to serialize.

        Returns:
            Any: A JSON-serializable version of the object.
        """
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

    def _validate_create(self, form_data: Dict[str, Any]) -> List[str]:
        """
        Validate data for creating a new item.

        Args:
            form_data (Dict[str, Any]): Submitted form or JSON data.

        Returns:
            List[str]: A list of validation error messages.
        """
        logger.debug(f"Validating create data for {self.model.__name__}")
        errors = []

        for field in self.required_fields:
            if field not in form_data or not form_data[field]:
                logger.warning(f"Required field '{field}' is missing or empty")
                errors.append(f"{field} is required.")

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

    def _validate_edit(self, item: Any, form_data: Dict[str, Any]) -> List[str]:
        """
        Validate data for editing an existing item.

        Args:
            item (Any): The existing model instance.
            form_data (Dict[str, Any]): Submitted form or JSON data.

        Returns:
            List[str]: A list of validation error messages.
        """
        logger.debug(
            f"Validating edit data for {self.model.__name__} with id {item.id}"
        )
        errors = []

        for field in self.required_fields:
            if field not in form_data or not form_data[field]:
                logger.warning(f"Required field '{field}' is missing or empty")
                errors.append(f"{field} is required.")

        for field in self.unique_fields:
            if field in form_data and form_data[field]:
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
        Validate if the given dictionary is fully JSON serializable.

        Args:
            data (Dict[str, Any]): The data to validate.
            path (str, optional): Used to track nested paths during recursion.

        Returns:
            List[str]: A list of paths where JSON serialization fails.
        """
        issues = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                try:
                    json.dumps({key: value})
                except TypeError as e:
                    logger.error(
                        f"JSON serialization error at {current_path}: {str(e)}"
                    )
                    issues.append(f"{current_path}: {type(value).__name__}")

                if isinstance(value, dict):
                    issues.extend(
                        self._validate_json_serializable(value, current_path)
                    )
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            issues.extend(
                                self._validate_json_serializable(item, f"{current_path}[{i}]")
                            )

        return issues
