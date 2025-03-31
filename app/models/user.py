import logging
from flask_login import UserMixin
from app.models.base import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from app.routes.base.components.form_handler import Tab, TabSection, TabEntry

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

    relationships = db.relationship("Relationship", back_populates="user", cascade="all, delete-orphan")
    notes = db.relationship("Note", backref="author", lazy="dynamic")


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


def to_dict(self):
    """Convert User instance to a dictionary for serialization.

    Returns:
        dict: Dictionary representation of the user.
    """
    base_dict = super().to_dict()

    # Include relationships from both directions
    from app.models.relationship import Relationship
    from app.services.relationship_service import RelationshipService

    # Get relationships where user is either entity1 or entity2
    entity1_relationships = Relationship.query.filter_by(
        entity1_type='user',
        entity1_id=self.id
    ).all()

    entity2_relationships = Relationship.query.filter_by(
        entity2_type='user',
        entity2_id=self.id
    ).all()

    # Process relationships to get related users and companies
    related_users = []
    related_companies = []

    for rel in entity1_relationships + entity2_relationships:
        # Determine the related entity (the one that's not this user)
        if rel.entity1_type == 'user' and rel.entity1_id == self.id:
            related_type = rel.entity2_type
            related_id = rel.entity2_id
        else:
            related_type = rel.entity1_type
            related_id = rel.entity1_id

        # Get the related entity
        related_entity = RelationshipService.get_entity(related_type, related_id)
        if not related_entity:
            continue

        # Add to appropriate list
        if related_type == 'user':
            related_users.append({
                'id': related_entity.id,
                'name': related_entity.name,
                'username': related_entity.username,
                'relationship_type': rel.relationship_type
            })
        elif related_type == 'company':
            related_companies.append({
                'id': related_entity.id,
                'name': related_entity.name,
                'relationship_type': rel.relationship_type
            })

    # Add the processed relationships to the dictionary
    base_dict['related_users'] = related_users
    base_dict['related_companies'] = related_companies

    return base_dict