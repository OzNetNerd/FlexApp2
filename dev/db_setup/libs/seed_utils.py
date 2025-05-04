# seed_utils.py - Utility functions for seeding

import logging
import sys
import os

from libs.path_utils import setup_paths

# Setup paths
root_dir, _ = setup_paths()

from app.models.base import db

logger = logging.getLogger(__name__)


def create_or_update(model, match_by: dict, data: dict):
    """Create or update an instance of the model based on the match criteria."""
    instance = model.query.filter_by(**match_by).first()
    if instance:
        # Update the instance with new data
        for key, value in data.items():
            setattr(instance, key, value)
        logger.info(f"Updated existing {model.__name__}: {match_by}")
    else:
        # Create a new instance if none found
        instance = model(**{**match_by, **data})
        db.session.add(instance)
        logger.info(f"Created new {model.__name__}: {match_by}")
    return instance


def safe_commit():
    """Safely commit changes to the database."""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing changes: {e}")
        return False
