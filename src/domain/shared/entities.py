"""Shared domain entities used across bounded contexts."""

from datetime import datetime


class BaseEntity:
    """
    Base entity with common attributes and methods for all entities.

    Attributes:
        id: Unique identifier.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    def __init__(self, id=None, created_at=None, updated_at=None):
        """
        Initialize a base entity.

        Args:
            id: Unique identifier.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        self.id = id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


class Note(BaseEntity):
    """
    A note entity that can be associated with various other entities.

    Represents a text note attached to any notable entity.

    Attributes:
        content: Note text content.
        processed_content: Processed version of content.
        user_id: ID of user who created the note.
        notable_type: Type of entity this note is attached to.
        notable_id: ID of entity this note is attached to.
    """

    def __init__(self, id=None, content=None, user_id=None, notable_type=None,
                 notable_id=None, processed_content=None, created_at=None, updated_at=None):
        """
        Initialize a note.

        Args:
            id: Unique identifier.
            content: Note text content (required).
            user_id: ID of user who created the note (required).
            notable_type: Type of entity this note is attached to.
            notable_id: ID of entity this note is attached to.
            processed_content: Processed version of content.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.content = content
        self.processed_content = processed_content
        self.user_id = user_id
        self.notable_type = notable_type
        self.notable_id = notable_id

    def __repr__(self) -> str:
        """Return string representation of the note."""
        return f"<Note {self.id} on {self.notable_type} {self.notable_id}>"


class Task(BaseEntity):
    """
    A task entity that can be associated with various other entities.

    Represents an actionable task that may be assigned to users.

    Attributes:
        title: Task title.
        description: Task description.
        due_date: Task due date.
        status: Current status.
        priority: Task priority.
        assigned_to_id: ID of user assigned to this task.
        completed_at: Timestamp when task was completed.
        notable_type: Type of entity this task is attached to.
        notable_id: ID of entity this task is attached to.
    """

    STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"]
    PRIORITIES = ["Low", "Medium", "High", "Urgent"]

    def __init__(self, id=None, title=None, description=None, due_date=None,
                 status="Pending", priority="Medium", assigned_to_id=None,
                 notable_type=None, notable_id=None, completed_at=None,
                 created_at=None, updated_at=None):
        """
        Initialize a task.

        Args:
            id: Unique identifier.
            title: Task title (required).
            description: Task description.
            due_date: Task due date.
            status: Current status.
            priority: Task priority.
            assigned_to_id: ID of user assigned to this task.
            notable_type: Type of entity this task is attached to.
            notable_id: ID of entity this task is attached to.
            completed_at: Timestamp when task was completed.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.title = title
        self.description = description
        self.due_date = due_date
        self._status = None
        self.status = status
        self._priority = None
        self.priority = priority
        self.assigned_to_id = assigned_to_id
        self.completed_at = completed_at
        self.notable_type = notable_type
        self.notable_id = notable_id

    @property
    def status(self):
        """Get the task status."""
        return self._status

    @status.setter
    def status(self, value):
        """
        Set the task status, handling the completed_at timestamp.

        Args:
            value: Status value.

        Raises:
            ValueError: If status is not valid.
        """
        if value and value not in self.STATUSES:
            raise ValueError(f"Invalid status: {value}. Must be one of {self.STATUSES}")

        # Handle completed_at timestamp
        if value == "Completed" and not self.completed_at:
            self.completed_at = datetime.now()
        elif value != "Completed" and self.completed_at:
            self.completed_at = None

        self._status = value

    @property
    def priority(self):
        """Get the task priority."""
        return self._priority

    @priority.setter
    def priority(self, value):
        """
        Set the task priority, validating against allowed priorities.

        Args:
            value: Priority value.

        Raises:
            ValueError: If priority is not valid.
        """
        if value and value not in self.PRIORITIES:
            raise ValueError(f"Invalid priority: {value}. Must be one of {self.PRIORITIES}")
        self._priority = value

    @property
    def is_overdue(self) -> bool:
        """
        Check if task is overdue.

        Returns:
            bool: True if due date is in the past and task is not completed.
        """
        return (self.due_date is not None and
                self.due_date < datetime.now() and
                self.status != "Completed")

    def complete(self):
        """Mark the task as completed."""
        self.status = "Completed"

    def __repr__(self) -> str:
        """Return string representation of the task."""
        return f"<Task {self.title!r}>"


class Relationship(BaseEntity):
    """
    A relationship entity connecting two entities of any type.

    Used to model flexible relationships between different domain entities.

    Attributes:
        entity1_type: Type of the first entity.
        entity1_id: ID of the first entity.
        entity2_type: Type of the second entity.
        entity2_id: ID of the second entity.
        relationship_type: Type of relationship (e.g., manager, linked).
    """

    def __init__(self, id=None, entity1_type=None, entity1_id=None,
                 entity2_type=None, entity2_id=None, relationship_type=None,
                 created_at=None, updated_at=None):
        """
        Initialize a relationship.

        Args:
            id: Unique identifier.
            entity1_type: Type of the first entity.
            entity1_id: ID of the first entity.
            entity2_type: Type of the second entity.
            entity2_id: ID of the second entity.
            relationship_type: Type of relationship.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.entity1_type = entity1_type
        self.entity1_id = entity1_id
        self.entity2_type = entity2_type
        self.entity2_id = entity2_id
        self.relationship_type = relationship_type


class Crisp(BaseEntity):
    """
    A CRISP scoring entity for relationship trust evaluation.

    Measures Credibility, Reliability, Intimacy, and Self-orientation
    for a relationship between entities.

    Attributes:
        relationship_id: ID of the relationship being evaluated.
        credibility: Credibility score (0-10).
        reliability: Reliability score (0-10).
        intimacy: Intimacy score (0-10).
        self_orientation: Self-orientation score (0-10).
        notes: Additional notes about the evaluation.
        total_score: Calculated total CRISP score.
    """

    def __init__(self, id=None, relationship_id=None, credibility=0, reliability=0,
                 intimacy=0, self_orientation=0, notes=None, total_score=None,
                 created_at=None, updated_at=None):
        """
        Initialize a CRISP score.

        Args:
            id: Unique identifier.
            relationship_id: ID of the relationship being evaluated.
            credibility: Credibility score (0-10).
            reliability: Reliability score (0-10).
            intimacy: Intimacy score (0-10).
            self_orientation: Self-orientation score (0-10).
            notes: Additional notes about the evaluation.
            total_score: Calculated total CRISP score.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.relationship_id = relationship_id
        self.credibility = credibility
        self.reliability = reliability
        self.intimacy = intimacy
        self.self_orientation = self_orientation
        self.notes = notes
        self._total_score = total_score

    def calculate_total(self) -> float:
        """
        Calculate the CRISP total score using the standard formula.

        Formula:
            (C + R + I) / S, where S is self-orientation.
            If S is zero, it falls back to sum of other metrics.

        Returns:
            float: Calculated CRISP score.
        """
        c = self.credibility
        r = self.reliability
        i = self.intimacy
        s = self.self_orientation

        if s == 0:
            self._total_score = float(c + r + i)
        else:
            self._total_score = float(c + r + i) / s

        return self._total_score

    @property
    def total_score(self) -> float:
        """
        Get the total CRISP score, calculating it if needed.

        Returns:
            float: Total CRISP score.
        """
        if self._total_score is None:
            return self.calculate_total()
        return self._total_score

    def __repr__(self) -> str:
        """Return string representation of the CRISP score."""
        return f"<Crisp Relationship={self.relationship_id} Total={self.total_score}>"