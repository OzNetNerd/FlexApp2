# relationship.py

import logging
from app.models.base import db, BaseModel

logger = logging.getLogger(__name__)


class Relationship(BaseModel):
    """Represents a relationship between two entities in the CRM system."""

    __tablename__ = "relationships"

    # Generic entity fields
    entity1_type = db.Column(db.String(50), nullable=False)
    entity1_id = db.Column(db.Integer, nullable=False)
    entity2_type = db.Column(db.String(50), nullable=False)
    entity2_id = db.Column(db.Integer, nullable=False)
    relationship_type = db.Column(db.String(50), nullable=True)

    # Relationships
    user = db.relationship(
        "User",
        foreign_keys=[entity1_id],
        primaryjoin="and_(Relationship.entity1_id==User.id, Relationship.entity1_type=='user')",
        back_populates="relationships",
        overlaps="contact",
    )

    contact = db.relationship(
        "Contact",
        foreign_keys=[entity1_id],
        primaryjoin="and_(Relationship.entity1_id==Contact.id, Relationship.entity1_type=='contact')",
        back_populates="relationships",
        overlaps="user",
    )

    # CRISP scores relationship
    crisp_scores = db.relationship("CRISPScore", back_populates="relationship", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint(
            "entity1_type", "entity1_id", "entity2_type", "entity2_id", "relationship_type", name="_entity_relationship_uc"
        ),
    )

    def __repr__(self) -> str:
        return f"<Relationship {self.entity1_type}={self.entity1_id} {self.relationship_type or '-'} {self.entity2_type}={self.entity2_id}>"

    @classmethod
    def create_relationship(cls, entity1_type, entity1_id, entity2_type, entity2_id, relationship_type=None):
        relationship = cls(
            entity1_type=entity1_type,
            entity1_id=entity1_id,
            entity2_type=entity2_type,
            entity2_id=entity2_id,
            relationship_type=relationship_type,
        )
        return relationship

    @classmethod
    def get_relationships(cls, entity_type, entity_id, related_entity_type=None):
        query = cls.query.filter(
            db.or_(
                db.and_(cls.entity1_type == entity_type, cls.entity1_id == entity_id),
                db.and_(cls.entity2_type == entity_type, cls.entity2_id == entity_id),
            )
        )
        if related_entity_type:
            query = query.filter(db.or_(cls.entity1_type == related_entity_type, cls.entity2_type == related_entity_type))
        return query.all()

    def get_related_entity(self, from_entity_type, from_entity_id):
        if self.entity1_type == from_entity_type and self.entity1_id == from_entity_id:
            return self.entity2_type, self.entity2_id
        else:
            return self.entity1_type, self.entity1_id
