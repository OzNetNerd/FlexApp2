# app/utils/model_registry.py
from flask import current_app


def get_model_by_name(name):
    """Get model class by its entity name."""
    from app.models import Company, Contact  # Import all your models

    models = {
        'Company': Company,
        'Contact': Contact,
        # Add other models
    }

    if name not in models:
        current_app.logger.error(f"Model {name} not found in registry")
        raise ValueError(f"Unknown model: {name}")

    return models[name]