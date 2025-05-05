"""Company domain entities."""

from src.domain.shared.entities import BaseEntity


class Company(BaseEntity):
    """
    A company entity representing a business organization.

    Attributes:
        name: The company name.
        description: Optional company description.
    """

    def __init__(self, id=None, name=None, description=None, created_at=None, updated_at=None):
        """
        Initialize a company entity.

        Args:
            id: Unique identifier for the company.
            name: Company name (required).
            description: Company description (optional).
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        """Return string representation of the company."""
        return f"<Company {self.name!r}>"


class CompanyCapability(BaseEntity):
    """
    Represents a specific capability or expertise area of a company.

    A bridge entity between Company and Capability entities.
    """

    def __init__(self, id=None, company_id=None, capability_id=None, level=None, created_at=None, updated_at=None):
        """
        Initialize a company capability.

        Args:
            id: Unique identifier.
            company_id: ID of the associated company.
            capability_id: ID of the capability.
            level: Proficiency level for this capability.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.company_id = company_id
        self.capability_id = capability_id
        self.level = level
