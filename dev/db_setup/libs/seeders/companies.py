# seeders/companies.py - Company seeder

import logging

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit
from libs.seed_data import COMPANIES

# Setup paths
root_dir, _ = setup_paths()

from app.models import Company

logger = logging.getLogger(__name__)

def seed_companies():
    """Seed companies into the database."""
    for name, description in COMPANIES:
        create_or_update(Company, {"name": name}, {"description": description})
    safe_commit()
    logger.info("✅ Companies seeded.")