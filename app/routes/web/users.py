# app/routes/web/users.py

from app.models import User, Note
from app.routes.web import users_bp
from app.routes.web.generic import GenericWebRoutes
import logging
from app.routes.ui.users import get_users_tabs
from app.services.relationship_service import RelationshipService
from typing import List
from app.routes.base.components.form_handler import AutoCompleteField

logger = logging.getLogger(__name__)

# Create a custom CRUD routes class for Users
class UserCRUDRoutes(GenericWebRoutes):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_view_context(self, item, context):
        """Add notes_model and relationships to the view context."""
        logger.debug(f"Adding 'notes_model' to the view context for User {item.id}.")
        context["notes_model"] = Note

        # Add relationships context
        logger.debug(f"Adding relationships to the view context for User {item.id}.")
        relationships = RelationshipService.get_relationships_for_entity('user', item.id)
        context["relationships"] = relationships

        # Add autocomplete fields for mappings
        self._add_autocomplete_fields(item, context, relationships)

    def add_edit_context(self, item, context):
        """Add autocomplete fields to the edit context."""
        # Call the parent method first
        super().add_edit_context(item, context)

        # Get relationships for this user
        logger.debug(f"Adding autocomplete fields to edit context for User {item.id}")
        relationships = RelationshipService.get_relationships_for_entity('user', item.id)

        # Extract related user and company IDs from relationships
        related_user_ids = []
        related_company_ids = []

        for rel in relationships:
            if rel['entity_type'] == 'user':
                related_user_ids.append(rel['entity_id'])
            elif rel['entity_type'] == 'company':
                related_company_ids.append(rel['entity_id'])

        # Add autocomplete fields configuration
        context["autocomplete_fields"] = [
            AutoCompleteField(
                title="Users",
                id="users-input",
                placeholder="Search for users...",
                name="users",
                data_url="/users/data",
                initial_ids=related_user_ids
            ),
            AutoCompleteField(
                title="Companies",
                id="companies-input",
                placeholder="Search for companies...",
                name="companies",
                data_url="/companies/data",
                initial_ids=related_company_ids
            )
        ]

        logger.debug(f"Added {len(context['autocomplete_fields'])} autocomplete fields to context")

    @staticmethod
    def _add_autocomplete_fields(item, context, relationships):
        """Helper method to add autocomplete fields to context"""
        # Extract related user and company IDs from relationships
        related_user_ids = []
        related_company_ids = []

        for rel in relationships:
            if rel['entity_type'] == 'user':
                related_user_ids.append(rel['entity_id'])
            elif rel['entity_type'] == 'company':
                related_company_ids.append(rel['entity_id'])

        # Add autocomplete fields configuration
        context["autocomplete_fields"] = [
            {
                "title": "Users",
                "id": "users-input",
                "placeholder": "Search for users...",
                "name": "users",
                "data_url": "/api/users/autocomplete",
                "initial_ids": related_user_ids
            },
            {
                "title": "Companies",
                "id": "companies-input",
                "placeholder": "Search for companies...",
                "name": "companies",
                "data_url": "/api/companies/autocomplete",
                "initial_ids": related_company_ids
            }
        ]

        logger.debug(f"Added {len(context['autocomplete_fields'])} autocomplete fields to context")


# Set up the CRUD routes for users
logger.debug("Setting up CRUD routes for User model.")
user_routes = UserCRUDRoutes(
    model=User,
    blueprint=users_bp,
    index_template="entity_tables/users.html",
    required_fields=["username", "name", "email"],
    unique_fields=["username"],
    get_tabs_function=get_users_tabs,
)

logger.info("User CRUD routes setup successfully.")