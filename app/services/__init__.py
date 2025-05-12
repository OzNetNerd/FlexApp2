"""Service registry and initialization module for the application."""

# Service imports
from app.services.srs import SRSService
from app.services.auth import AuthService
from app.services.category_service import CategoryService
from app.services.company_service import CompanyService
from app.services.contact_service import ContactService
from app.services.crud_service import CRUDService
from app.services.note_service import NoteService
from app.services.opportunity_service import OpportunityService
from app.services.relationship_service import RelationshipService
from app.services.search_service import SearchService
from app.services.task_service import TaskService
from app.services.user_service import UserService

# Utility imports
from app.utils.app_logging import get_logger

# Setup logging
logger = get_logger()
logger.info("Initializing services module.")

# Create a registry of services for easy access
service_registry = {
    'srs': SRSService(),
    'auth': AuthService(),
    'category': CategoryService(),
    'company': CompanyService(),
    'contact': ContactService(),
    'crud': CRUDService(),
    'note': NoteService(),
    'opportunity': OpportunityService(),
    'relationship': RelationshipService(),
    'search': SearchService(),
    'task': TaskService(),
    'user': UserService(),
}


def init_db(app):
    """Initialize the database with the Flask app"""
    # Import here to avoid circular imports
    from create_db import init_db as setup_db

    # Call the actual setup function
    setup_db(app)


# Helper function to get service instances
def get_service(service_name):
    """
    Get a service instance by name.

    Args:
        service_name: Name of the service to retrieve

    Returns:
        Service instance

    Raises:
        ValueError: If the service name is not registered
    """
    if service_name not in service_registry:
        raise ValueError(f"Service '{service_name}' not found in registry")

    return service_registry[service_name]


# Create convenience getters for common services
def get_srs_service():
    """Get the SRS service instance."""
    return service_registry['srs']


def get_auth_service():
    """Get the Auth service instance."""
    return service_registry['auth']


def get_company_service():
    """Get the Company service instance."""
    return service_registry['company']


def get_contact_service():
    """Get the Contact service instance."""
    return service_registry['contact']


def get_opportunity_service():
    """Get the Opportunity service instance."""
    return service_registry['opportunity']


def get_user_service():
    """Get the User service instance."""
    return service_registry['user']


# Export all necessary functions and classes
__all__ = [
    "init_db",
    "CRUDService",
    "get_service",
    "get_srs_service",
    "get_auth_service",
    "get_company_service",
    "get_contact_service",
    "get_opportunity_service",
    "get_user_service"
]