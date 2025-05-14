# app/utils/model_registry.py
from flask import current_app
import app.models as models


def get_model_by_name(name):
    """Get model class by its entity name."""
    # Try exact match first
    if name in models.__all__:
        return getattr(models, name)

    # Try case-insensitive match
    for model_name in models.__all__:
        if model_name.lower() == name.lower():
            return getattr(models, model_name)

    current_app.logger.error(f"Model {name} not found in registry")
    raise ValueError(f"Unknown model: {name}")