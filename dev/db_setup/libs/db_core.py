# db_core.py - Core database setup functions

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from libs.path_utils import get_root_dir

logger = logging.getLogger(__name__)

# Import models
root_dir = get_root_dir()
sys.path.append(root_dir)

from app.models.base import db

def setup_db():
    """Setup the database connection without using Flask"""
    # Use crm.db in the root directory
    db_path = "sqlite:///" + os.path.join(root_dir, "crm.db")
    logger.info(f"Initializing database at: {db_path}")

    # Check if database file exists
    db_file = os.path.join(root_dir, "crm.db")
    db_exists = os.path.exists(db_file)

    if not db_exists:
        logger.info("Creating new database...")
        # Ensure the database directory exists
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
    else:
        logger.info("Database already exists, updating as needed...")

    # Create engine and session
    engine = create_engine(db_path)
    db.Model.metadata.create_all(engine)

    # Create a session
    session = scoped_session(sessionmaker(bind=engine))
    db.session = session

    return db_file