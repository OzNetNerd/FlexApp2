from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

# Log that the modules have been imported and initialized
logger.info("Initializing services module.")


# Don't import anything here - we'll define the init_db function that will be imported by app.py
def init_db(app):
    """Initialize the database with the Flask app"""
    # Import here to avoid circular imports
    from create_db import init_db as setup_db

    # Call the actual setup function
    setup_db(app)


# Expose other functions that don't cause circular imports
# from .mention import process_mentions

# __all__ = ["init_db", "process_mentions"]
__all__ = ["init_db", "CRUDService"]