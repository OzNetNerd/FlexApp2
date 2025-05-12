"""Service registry and initialization module for the application."""

# Base service imports
from app.services.service_base import ServiceRegistry

# Service imports
from app.services.srs import SRSService
from app.services.auth import AuthService
from app.services.company import CompanyService
from app.services.contact import ContactService
# from app.services.crud import CRUDService
from app.services.note import NoteService
from app.services.opportunity import OpportunityService
from app.services.relationship import RelationshipService
from app.services.search import SearchService
from app.services.task import TaskService
from app.services.user import UserService

# Utility imports
from app.utils.app_logging import get_logger

# Setup logging
logger = get_logger()
logger.info("Initializing services module.")

# Create a registry of services for easy access
service_registry = {
    'srs': ServiceRegistry.get(SRSService),
    'auth': ServiceRegistry.get(AuthService),
    # 'category': ServiceRegistry.get(CategoryService),
    'company': ServiceRegistry.get(CompanyService),
    'contact': ServiceRegistry.get(ContactService),
    # 'crud': ServiceRegistry.get(CRUDService),
    'note': ServiceRegistry.get(NoteService),
    'opportunity': ServiceRegistry.get(OpportunityService),
    'relationship': ServiceRegistry.get(RelationshipService),
    'search': ServiceRegistry.get(SearchService),
    'task': ServiceRegistry.get(TaskService),
    'user': ServiceRegistry.get(UserService),
}


def init_db(app):
    """Initialize the database with the Flask app"""
    from create_db import init_db as setup_db
    setup_db(app)


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