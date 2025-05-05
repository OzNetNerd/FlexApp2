"""Opportunity domain entities."""

from datetime import datetime
from src.domain.shared.entities import BaseEntity
from src.domain.shared.value_objects.money import Money


class Opportunity(BaseEntity):
    """
    An opportunity entity representing a potential business deal.

    Tracks sales opportunities with companies and contacts.

    Attributes:
        name: Opportunity name.
        description: Opportunity description.
        status: Current status (active, closed, etc).
        stage: Sales pipeline stage.
        value: Potential monetary value.
        priority: Business priority level.
        close_date: Expected closing date.
        company_id: Associated company identifier.
    """

    STAGES = ["qualification", "proposal", "negotiation", "closed_won", "closed_lost"]
    STATUSES = ["active", "inactive", "on_hold", "closed"]
    PRIORITIES = ["low", "medium", "high", "critical"]

    def __init__(
        self,
        id=None,
        name=None,
        description=None,
        status="active",
        stage="qualification",
        value=0.0,
        priority="medium",
        close_date=None,
        created_by_id=None,
        company_id=None,
        created_at=None,
        updated_at=None,
    ):
        """
        Initialize an opportunity.

        Args:
            id: Unique identifier.
            name: Opportunity name (required).
            description: Opportunity description.
            status: Current status (active, inactive, on_hold, closed).
            stage: Sales pipeline stage.
            value: Potential monetary value.
            priority: Business priority level.
            close_date: Expected closing date.
            created_by_id: ID of user who created the opportunity.
            company_id: ID of associated company.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
        self._status = None
        self.status = status
        self._stage = None
        self.stage = stage
        self._value = None
        self.value = value
        self._priority = None
        self.priority = priority
        self.close_date = close_date
        self.last_activity_date = datetime.now()
        self.created_by_id = created_by_id
        self.company_id = company_id

    @property
    def status(self):
        """Get the opportunity status."""
        return self._status

    @status.setter
    def status(self, value):
        """
        Set the opportunity status, validating against allowed statuses.

        Args:
            value: Status value.

        Raises:
            ValueError: If status is not valid.
        """
        if value and value not in self.STATUSES:
            raise ValueError(f"Invalid status: {value}. Must be one of {self.STATUSES}")
        self._status = value

    @property
    def stage(self):
        """Get the opportunity stage."""
        return self._stage

    @stage.setter
    def stage(self, value):
        """
        Set the opportunity stage, validating against allowed stages.

        Args:
            value: Stage value.

        Raises:
            ValueError: If stage is not valid.
        """
        if value and value not in self.STAGES:
            raise ValueError(f"Invalid stage: {value}. Must be one of {self.STAGES}")
        self._stage = value

    @property
    def priority(self):
        """Get the opportunity priority."""
        return self._priority

    @priority.setter
    def priority(self, value):
        """
        Set the opportunity priority, validating against allowed priorities.

        Args:
            value: Priority value.

        Raises:
            ValueError: If priority is not valid.
        """
        if value and value not in self.PRIORITIES:
            raise ValueError(f"Invalid priority: {value}. Must be one of {self.PRIORITIES}")
        self._priority = value

    @property
    def value(self):
        """Get the opportunity value as a Money object."""
        return self._value

    @value.setter
    def value(self, amount):
        """
        Set the opportunity value as a Money value object.

        Args:
            amount: Numeric value amount.
        """
        if amount is not None:
            self._value = Money(amount)

    def advance_stage(self):
        """
        Advance the opportunity to the next stage in the pipeline.

        Returns:
            bool: True if advanced, False if already at final stage.
        """
        current_index = self.STAGES.index(self.stage)
        if current_index < len(self.STAGES) - 1:
            self.stage = self.STAGES[current_index + 1]
            self.last_activity_date = datetime.now()
            return True
        return False

    def win(self):
        """Mark the opportunity as won."""
        self.stage = "closed_won"
        self.status = "closed"
        self.last_activity_date = datetime.now()

    def lose(self):
        """Mark the opportunity as lost."""
        self.stage = "closed_lost"
        self.status = "closed"
        self.last_activity_date = datetime.now()

    def __repr__(self) -> str:
        """Return string representation of the opportunity."""
        return f"<Opportunity {self.name!r}>"
