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
    # Log root directory being used
    logger.info(f"Using root directory: {root_dir}")

    # Use crm.db in the root directory
    db_file = os.path.join(root_dir, "crm.db")
    db_path = "sqlite:///" + db_file
    logger.info(f"Database file will be created at: {db_file}")
    logger.info(f"SQLAlchemy connection string: {db_path}")

    # Check if database file exists
    db_exists = os.path.exists(db_file)
    logger.info(f"Database file exists: {db_exists}")

    # Get database directory and log it
    db_dir = os.path.dirname(db_file)
    logger.info(f"Database directory: {db_dir}")

    # Check if directory exists and log result
    dir_exists = os.path.exists(db_dir) if db_dir else True
    logger.info(f"Database directory exists: {dir_exists}")

    if not db_exists:
        logger.info("Creating new database...")
        # Ensure the database directory exists
        if db_dir:
            # Force directory creation with exist_ok=True
            logger.info(f"Attempting to create directory: {db_dir}")
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.error(f"Error creating directory: {e}")
    else:
        logger.info("Database already exists, updating as needed...")

    # Log before engine creation
    logger.info("Creating SQLAlchemy engine...")

    # Create engine and session
    try:
        engine = create_engine(db_path)
        logger.info("Engine created successfully")

        logger.info("Creating database tables...")
        db.Model.metadata.create_all(engine)
        logger.info("Tables created successfully")

        # Create a session
        logger.info("Creating database session...")
        session = scoped_session(sessionmaker(bind=engine))
        db.session = session
        logger.info("Session created successfully")
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise

    return db_file