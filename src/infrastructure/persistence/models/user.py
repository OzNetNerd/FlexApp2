"""User ORM model for authentication and authorization."""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from src.infrastructure.persistence.models.base import BaseModel
from src.infrastructure.flask.extensions import db


class User(BaseModel, UserMixin):
    """
    ORM model for users.

    Provides authentication and authorization functionality.
    """

    __tablename__ = "users"

    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Explicit foreign key and primaryjoin for relationships
    relationships = db.relationship(
        "Relationship",
        foreign_keys="[Relationship.entity1_id]",
        primaryjoin="and_(User.id == Relationship.entity1_id, "
                    "Relationship.entity1_type == 'user')",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="contact",
    )

    notes = db.relationship("Note", backref="author", lazy="dynamic")

    def __init__(self, *args, **kwargs):
        """
        Initialize a user with password hashing.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments, including 'password'.
        """
        password = kwargs.pop("password", None)
        super().__init__(*args, **kwargs)
        if password:
            self.set_password(password)

    def set_password(self, password):
        """
        Set the user's password, hashing it securely.

        Args:
            password: Plain text password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hash.

        Args:
            password: Plain text password to check.

        Returns:
            bool: True if password matches.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Return string representation of the user."""
        return f"<User {self.username}>"