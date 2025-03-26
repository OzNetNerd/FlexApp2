import logging
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app.models.base import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)


class User(BaseModel, UserMixin):
    """Represents a CRM system user.

    Supports authentication and permission logic, and links to notes
    and contact relationships for CRISP scoring.

    Attributes:
        username (str): Unique login identifier.
        name (str): Full display name.
        email (str): Unique email address.
        password_hash (str): Hashed password for login.
        is_admin (bool): Flag for admin users.
        relationships (list[Relationship]): Connections to contacts.
        notes (list[Note]): Authored notes.
    """

    __tablename__ = "users"

    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    relationships = db.relationship(
        "Relationship", back_populates="user", cascade="all, delete-orphan"
    )
    notes = db.relationship("Note", backref="author", lazy="dynamic")

    __field_order__ = [
        {
            "name": "username", "label": "Username", "type": "text",
            "tab": "About", "section": "Basic Info", "required": True
        },
        {
            "name": "name", "label": "Name", "type": "text",
            "tab": "About", "section": "Basic Info", "required": True
        },
        {
            "name": "email", "label": "Email", "type": "email",
            "tab": "About", "section": "Contact", "required": True
        },
        {
            "name": "created_at", "label": "Created At", "type": "datetime",
            "readonly": True, "tab": "About", "section": "Record Info"
        },
        {
            "name": "updated_at", "label": "Updated At", "type": "datetime",
            "readonly": True, "tab": "About", "section": "Record Info"
        },
        {
            "name": "crisp", "label": "CRISP", "type": "custom",
            "tab": "Insights", "section": "CRISP Score"
        },
    ]

    def __init__(self, *args, **kwargs):
        """Initialize user, allowing plain-text 'password' for hashing."""
        password = kwargs.pop("password", None)
        super().__init__(*args, **kwargs)
        if password:
            logger.debug("Hashing password before saving user.")
            self.password_hash = generate_password_hash(password)

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: User's username.
        """
        return f"<User {self.username}>"

    @staticmethod
    def search_by_username(query: str) -> list:
        """Search for users by partial username match.

        Args:
            query (str): Starting characters of the username.

        Returns:
            list: User objects matching the query.
        """
        logger.debug(f"Searching for users with username starting with '{query}'")
        result = User.query.filter(User.username.ilike(f"{query}%")).all()
        logger.debug(f"Found {len(result)} users matching the query '{query}'")
        return result

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash.

        Args:
            password (str): Plaintext password to verify.

        Returns:
            bool: True if password is valid, False otherwise.
        """
        return check_password_hash(self.password_hash, password)