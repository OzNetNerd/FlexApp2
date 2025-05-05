"""ORM models for the customer domain."""

from src.infrastructure.persistence.models.base import BaseModel
from src.infrastructure.flask.extensions import db


class Contact(BaseModel):
    """
    ORM model for contacts.

    Maps the Contact domain entity to the database.
    """

    __tablename__ = "contacts"

    # --- Contact Information ---
    first_name = db.Column(db.String(127), nullable=False)
    last_name = db.Column(db.String(127), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(50))
    role = db.Column(db.String(255))
    role_level = db.Column(db.String(50))

    # Link Contact to a Company
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    company = db.relationship("Company", back_populates="contacts")

    # --- Role and Responsibilities ---
    team_roles_responsibilities = db.Column(db.Text)
    role_description = db.Column(db.Text)
    responsibilities = db.Column(db.Text)

    # --- Skill Level ---
    primary_skill_area = db.Column(db.String(50))
    skill_level = db.Column(db.String(50))
    certifications = db.Column(db.Text)

    # --- Technologies Used ---
    cloud_platforms = db.Column(db.Text)
    devops_tools = db.Column(db.Text)
    version_control_systems = db.Column(db.Text)
    programming_languages = db.Column(db.Text)
    monitoring_logging = db.Column(db.Text)
    ci_cd_tools = db.Column(db.Text)
    other_technologies = db.Column(db.Text)

    # --- Expertise & Projects ---
    expertise_areas = db.Column(db.String(255))
    technologies_led = db.Column(db.Text)

    # --- Relationships ---
    relationships = db.relationship(
        "Relationship",
        primaryjoin="and_(foreign(Relationship.entity1_id)==Contact.id, "
                    "Relationship.entity1_type=='contact')",
        back_populates="contact",
        overlaps="user,relationships",
    )

    opportunity_relationships = db.relationship(
        "Relationship",
        primaryjoin="and_(or_(and_(Relationship.entity1_type=='contact', "
                    "foreign(Relationship.entity1_id)==Contact.id, "
                    "Relationship.entity2_type=='opportunity'), "
                    "and_(Relationship.entity2_type=='contact', "
                    "foreign(Relationship.entity2_id)==Contact.id, "
                    "Relationship.entity1_type=='opportunity')))",
        viewonly=True,
    )

    tasks = db.relationship(
        "Task",
        primaryjoin="and_(Task.notable_type=='contact', "
                    "foreign(Task.notable_id)==Contact.id)",
        backref="contact",
        lazy="dynamic"
    )

    notes = db.relationship(
        "Note",
        primaryjoin="and_(Note.notable_type=='Contact', "
                    "foreign(Note.notable_id)==Contact.id)",
        backref="contact"
    )

    @property
    def full_name(self):
        """Get the contact's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        """Return string representation of the contact."""
        return f"<Contact {self.id} {self.full_name}>"