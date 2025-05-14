# app/models/user.py

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.base import BaseModel, db
from app.models.relationship import Relationship
from app.utils.app_logging import get_logger

logger = get_logger()


class User(BaseModel, UserMixin):
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
        primaryjoin="and_(User.id == Relationship.entity1_id, Relationship.entity1_type == 'user')",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="contact",
    )

    notes = db.relationship("Note", backref="author", lazy="dynamic")

    def __init__(self, *args, **kwargs):
        password = kwargs.pop("password", None)
        super().__init__(*args, **kwargs)
        if password:
            logger.info("Hashing password before saving user.")
            self.password_hash = generate_password_hash(password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    @staticmethod
    def search_by_username(query: str) -> list:
        result = User.query.filter(User.username.ilike(f"{query}%")).all()
        return result

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        from app.services.relationship import RelationshipService

        base_dict = super().to_dict()

        entity1_relationships = Relationship.query.filter_by(entity1_type="user", entity1_id=self.id).all()
        entity2_relationships = Relationship.query.filter_by(entity2_type="user", entity2_id=self.id).all()

        related_users = []
        related_companies = []

        for rel in entity1_relationships + entity2_relationships:
            if rel.entity1_type == "user" and rel.entity1_id == self.id:
                related_type = rel.entity2_type
                related_id = rel.entity2_id
            else:
                related_type = rel.entity1_type
                related_id = rel.entity1_id

            related_entity = RelationshipService.get_entity(related_type, related_id)
            if not related_entity:
                continue

            if related_type == "user":
                related_users.append(f"{related_entity.name} ({rel.relationship_type})")
            elif related_type == "company":
                related_companies.append(f"{related_entity.name} ({rel.relationship_type})")

        # Join lists into a comma-separated string.
        base_dict["related_users"] = ", ".join(related_users)
        base_dict["related_companies"] = ", ".join(related_companies)

        return base_dict
