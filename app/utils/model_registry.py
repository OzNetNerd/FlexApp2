# app/utils/model_registry.py
from flask import current_app
import app.models as models


def get_model_by_name(name):
    """Get model class by its entity name."""
    if name not in models.__all__:
        current_app.logger.error(f"Model {name} not found in registry")
        raise ValueError(f"Unknown model: {name}")

    return getattr(models, name)