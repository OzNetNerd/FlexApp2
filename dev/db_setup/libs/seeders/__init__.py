# seeders/__init__.py - Seeders package

import logging
from sqlalchemy.exc import IntegrityError
import sys
import os

from libs.path_utils import setup_paths

# Setup paths
root_dir, _ = setup_paths()

from app.models.base import db

# Import all seeders
from .users import seed_users
from .companies import seed_companies
from .contacts import seed_contacts
from .capabilities import seed_capabilities_and_categories, seed_company_capabilities
from .opportunities import seed_opportunities
from .tasks import seed_tasks
from .notes import seed_notes
from .relationships import seed_relationships
from .srs import seed_srs_items

logger = logging.getLogger(__name__)


def run_all_seeders():
    """Run all seeder functions in the correct order."""
    seeders = [
        seed_users,
        seed_companies,
        seed_contacts,
        seed_capabilities_and_categories,
        seed_company_capabilities,
        seed_opportunities,
        seed_tasks,
        seed_notes,
        seed_relationships,
        seed_srs_items,
    ]

    for seeder in seeders:
        seeder_name = seeder.__name__
        logger.info(f"Running seeder: {seeder_name}")
        try:
            seeder()  # Call the seed function
            logger.info(f"🎉 {seeder_name} completed successfully")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"❌ {seeder_name} IntegrityError: {e}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ {seeder_name} Error: {e}")
