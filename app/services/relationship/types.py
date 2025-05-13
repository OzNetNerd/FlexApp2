# app/services/relationship/types.py
from typing import List
from app.services.service_base import ServiceBase


class RelationshipTypeService(ServiceBase):
    """Service for relationship type management."""

    RELATIONSHIP_TYPES = {
        "user-user": ["Manager", "Colleague", "Direct Report", "Mentor"],
        "user-contact": ["Primary", "Secondary", "Support"],
        "user-company": ["Account Manager", "Sales Lead", "Support Lead"],
        "contact-company": ["Employee", "Executive", "Owner", "Board Member"],
        "company-company": ["Partner", "Supplier", "Customer", "Competitor"],
    }

    def __init__(self):
        super().__init__()

    def get_relationship_types(self, entity1_type: str, entity2_type: str) -> List[str]:
        """Get valid relationship types for two entity types."""
        key = f"{entity1_type.lower()}-{entity2_type.lower()}"
        reverse_key = f"{entity2_type.lower()}-{entity1_type.lower()}"

        if key in self.RELATIONSHIP_TYPES:
            return self.RELATIONSHIP_TYPES[key]
        elif reverse_key in self.RELATIONSHIP_TYPES:
            return self.RELATIONSHIP_TYPES[reverse_key]
        else:
            return []
