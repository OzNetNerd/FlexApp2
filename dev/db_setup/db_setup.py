#!/usr/bin/env python
# db_setup.py - Main database seeding coordinator

import os
import sys
import logging

# Add parent directory to path to access app
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Import modules from libs
from libs.db_core import setup_db
from libs.seeders import run_all_seeders

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Setup database
    db_file = setup_db()

    # Run all seeders
    run_all_seeders()

    logger.info(f"✅ Database setup complete: {db_file}")