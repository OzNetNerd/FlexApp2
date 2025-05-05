"""Customer domain entities."""

from src.domain.shared.entities import BaseEntity
from src.domain.shared.value_objects.email import Email
from src.domain.shared.value_objects.phone import Phone
from src.domain.shared.value_objects.relationship import Relationship


class Contact(BaseEntity):
    """
    A contact entity representing an individual associated with a company.

    Represents a person who may be involved in opportunities and has
    various professional attributes.

    Attributes:
        first_name: Contact's first name.
        last_name: Contact's last name.
        email: Contact's email address.
        phone_number: Contact's phone number.
        role: Job title or role.
        company_id: Associated company identifier.
        role_level: Seniority level.
    """

    def __init__(
        self,
        id=None,
        first_name=None,
        last_name=None,
        email=None,
        phone_number=None,
        role=None,
        role_level=None,
        company_id=None,
        created_at=None,
        updated_at=None,
    ):
        """
        Initialize a contact.

        Args:
            id: Unique identifier.
            first_name: Contact's first name (required).
            last_name: Contact's last name (required).
            email: Contact's email address (required).
            phone_number: Contact's phone number.
            role: Contact's job title.
            role_level: Contact's seniority level.
            company_id: ID of associated company.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.first_name = first_name
        self.last_name = last_name
        self._email = None
        self.email = email
        self._phone_number = None
        self.phone_number = phone_number
        self.role = role
        self.role_level = role_level
        self.company_id = company_id

        # Skills and expertise
        self.primary_skill_area = None
        self.skill_level = None
        self.certifications = None

        # Technologies
        self.cloud_platforms = None
        self.devops_tools = None
        self.programming_languages = None
        self.ci_cd_tools = None

    @property
    def full_name(self):
        """Get the contact's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def email(self):
        """Get the contact's email."""
        return self._email.value if self._email else None

    @email.setter
    def email(self, value):
        """
        Set the contact's email, validating it as an Email value object.

        Args:
            value: Email address string.
        """
        if value:
            self._email = Email(value)

    @property
    def phone_number(self):
        """Get the contact's phone number."""
        return self._phone_number.value if self._phone_number else None

    @phone_number.setter
    def phone_number(self, value):
        """
        Set the contact's phone number, validating it as a Phone value object.

        Args:
            value: Phone number string.
        """
        if value:
            self._phone_number = Phone(value)

    def __repr__(self) -> str:
        """Return string representation of the contact."""
        return f"<Contact {self.id} {self.full_name}>"


class Customer(BaseEntity):
    """
    A customer entity representing an organization or company.

    Attributes:
        name: Customer's company name.
        address: Physical address.
        company_relationships: Relationships with other entities.
    """

    def __init__(
        self,
        id=None,
        name=None,
        email=None,
        phone_number=None,
        address=None,
        company_relationships=None,
        created_at=None,
        updated_at=None,
    ):
        """
        Initialize a customer.

        Args:
            id: Unique identifier.
            name: Customer name (required).
            email: Customer main email address.
            phone_number: Customer main phone number.
            address: Physical address.
            company_relationships: Relationships with other companies.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.name = name
        self._email = None
        self.email = email
        self._phone_number = None
        self.phone_number = phone_number
        self.address = address
        self.company_relationships = company_relationships or []

    @property
    def email(self):
        """Get the customer's email."""
        return self._email.value if self._email else None

    @email.setter
    def email(self, value):
        """
        Set the customer's email, validating it as an Email value object.

        Args:
            value: Email address string.
        """
        if value:
            self._email = Email(value)

    @property
    def phone_number(self):
        """Get the customer's phone number."""
        return self._phone_number.value if self._phone_number else None

    @phone_number.setter
    def phone_number(self, value):
        """
        Set the customer's phone number, validating it as a Phone value object.

        Args:
            value: Phone number string.
        """
        if value:
            self._phone_number = Phone(value)

    def add_company_relationship(self, company_id, role=None, notes=None):
        """
        Add a relationship with another company.

        Args:
            company_id: ID of the related company.
            role: Relationship role or type.
            notes: Additional relationship notes.
        """
        relationship = Relationship(
            entity_id=company_id,
            entity_type="company",
            role=role,
            notes=notes
        )
        self.company_relationships.append(relationship)

    def __repr__(self) -> str:
        """Return string representation of the customer."""
        return f"<Customer {self.id} {self.name}>"