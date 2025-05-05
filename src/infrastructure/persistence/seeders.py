# src/infrastructure/persistence/seeders.py

"""
Database seeders.

This module contains functions to seed the database with initial data.
"""

from src.infrastructure.flask.extensions import db
from src.infrastructure.persistence.models.setting import Setting
from src.infrastructure.logging import get_logger

logger = get_logger()


def seed_database():
    """
    Seed the database with initial data.

    Creates all tables and seeds initial settings.
    """
    logger.info("Seeding settings and creating database tables.")
    Setting.seed()
    db.create_all()