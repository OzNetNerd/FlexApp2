import logging
from app.models.base import db, BaseModel
from sqlalchemy.ext.declarative import declared_attr

logger = logging.getLogger(__name__)


class Relationship(BaseModel):
    """Represents a relationship between two entities in the CRM system.

    This flexible model allows tracking of relationships between different entity types:
    - User ↔ Contact
    - User ↔ Company
    - Contact ↔ Company
    - User ↔ User

    Each relationship can have associated CRISP scores and other metadata.

    Attributes:
        entity1_type (str): Type of the first entity (user, contact, company, etc.)
        entity1_id (int): ID of the first entity
        entity2_type (str): Type of the second entity
        entity2_id (int): ID of the second entity
        relationship_type (str): Type of relationship (manager, client, etc.)
        crisp_scores (list[CRISPScore]): Historical trust scores for this relationship
    """

    __tablename__ = "relationships"

    # Generic entity fields
    entity1_type = db.Column(db.String(50), nullable=False)
    entity1_id = db.Column(db.Integer, nullable=False)
    entity2_type = db.Column(db.String(50), nullable=False)
    entity2_id = db.Column(db.Integer, nullable=False)
    relationship_type = db.Column(db.String(50), nullable=True)

    # Legacy fields to maintain compatibility
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=True)

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], back_populates="relationships")
    contact = db.relationship("Contact", foreign_keys=[contact_id], back_populates="relationships")

    # CRISP scores relationship
    crisp_scores = db.relationship("CRISPScore", back_populates="relationship", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("entity1_type", "entity1_id", "entity2_type", "entity2_id", "relationship_type",
                            name="_entity_relationship_uc"),
        # Keep legacy constraint for backward compatibility
        db.UniqueConstraint("user_id", "contact_id", name="_user_contact_uc"),
    )

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Details of the relationship between entities.
        """
        return f"<Relationship {self.entity1_type}={self.entity1_id} {self.relationship_type or '-'} {self.entity2_type}={self.entity2_id}>"

    @classmethod
    def create_relationship(cls, entity1_type, entity1_id, entity2_type, entity2_id, relationship_type=None):
        """Factory method to create a relationship between two entities.

        Args:
            entity1_type (str): Type of the first entity (user, contact, company)
            entity1_id (int): ID of the first entity
            entity2_type (str): Type of the second entity
            entity2_id (int): ID of the second entity
            relationship_type (str, optional): Type of relationship

        Returns:
            Relationship: The newly created relationship
        """
        relationship = cls(
            entity1_type=entity1_type,
            entity1_id=entity1_id,
            entity2_type=entity2_type,
            entity2_id=entity2_id,
            relationship_type=relationship_type
        )

        # For backward compatibility with legacy user-contact relationships
        if entity1_type == 'user' and entity2_type == 'contact':
            relationship.user_id = entity1_id
            relationship.contact_id = entity2_id

        return relationship

    @classmethod
    def get_relationships(cls, entity_type, entity_id, related_entity_type=None):
        """Get all relationships for a specific entity.

        Args:
            entity_type (str): Type of entity (user, contact, company)
            entity_id (int): ID of the entity
            related_entity_type (str, optional): Filter by related entity type

        Returns:
            list: List of relationship objects
        """
        query = cls.query.filter(
            db.or_(
                db.and_(cls.entity1_type == entity_type, cls.entity1_id == entity_id),
                db.and_(cls.entity2_type == entity_type, cls.entity2_id == entity_id)
            )
        )

        if related_entity_type:
            query = query.filter(
                db.or_(
                    cls.entity1_type == related_entity_type,
                    cls.entity2_type == related_entity_type
                )
            )

        return query.all()

    def get_related_entity(self, from_entity_type, from_entity_id):
        """Get the other entity in this relationship.

        Args:
            from_entity_type (str): Type of the source entity
            from_entity_id (int): ID of the source entity

        Returns:
            tuple: (entity_type, entity_id) of the related entity
        """
        if self.entity1_type == from_entity_type and self.entity1_id == from_entity_id:
            return (self.entity2_type, self.entity2_id)
        else:
            return (self.entity1_type, self.entity1_id)

    @classmethod
    def migrate_legacy_relationships(cls):
        """Migrate legacy user-contact relationships to the new format.

        This is a utility method to help with database migration.
        """
        relationships = cls.query.filter(
            db.and_(cls.user_id != None, cls.contact_id != None)
        ).all()

        for rel in relationships:
            if not rel.entity1_type:  # Only update if fields are empty
                rel.entity1_type = 'user'
                rel.entity1_id = rel.user_id
                rel.entity2_type = 'contact'
                rel.entity2_id = rel.contact_id
                rel.relationship_type = 'primary'  # Default type for legacy

        db.session.commit()

# Migration code to run (add to a migration script)
# from app.models.relationship import Relationship
# Relationship.migrate_legacy_relationships()