# contact.py

from app.models.base import db, BaseModel
from app.models.relationship import Relationship  # reuse the generic Relationship model

from app.utils.app_logging import get_logger

logger = get_logger()


class Contact(BaseModel):
    __tablename__ = "contacts"

    # --- Contact Information ---
    first_name = db.Column(db.String(127), nullable=False)
    last_name = db.Column(db.String(127), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(50))
    role = db.Column(db.String(255))
    role_level = db.Column(db.String(50))  # e.g., dropdown: Seniority levels

    # Link Contact to a Company via foreign key instead of a free-text company name.
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    company = db.relationship("Company", back_populates="contacts")

    # --- Role and Responsibilities ---
    team_roles_responsibilities = db.Column(db.Text)
    role_description = db.Column(db.Text)
    responsibilities = db.Column(db.Text)

    # --- Skill Level ---
    primary_skill_area = db.Column(db.String(50))  # dropdown: Cloud, DevOps, etc.
    skill_level = db.Column(db.String(50))  # dropdown: Beginner, Intermediate, Advanced, Expert
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
    # This property satisfies the back_populates in the Relationship model.
    # In Contact model:
    relationships = db.relationship(
        "Relationship",
        primaryjoin="and_(foreign(Relationship.entity1_id)==Contact.id, Relationship.entity1_type=='contact')",
        back_populates="contact",
        overlaps="user,relationships",  # Add "relationships" to the overlaps
    )

    # Tasks imported from the tasks table; assumes a Task model exists.
    tasks = db.relationship(
        "Task", primaryjoin="and_(Task.notable_type=='contact', foreign(Task.notable_id)==Contact.id)", backref="contact", lazy="dynamic"
    )

    # Notes using the polymorphic Note model.
    notes = db.relationship(
        "Note", primaryjoin="and_(Note.notable_type=='Contact', foreign(Note.notable_id)==Contact.id)", backref="contact"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # Computed properties to resolve relationships via the generic Relationship model.
    @property
    def opportunities(self):
        """
        Retrieve Opportunities linked to this Contact.
        Uses the Relationship model where this contact is linked to an opportunity.
        """
        from app.models.opportunity import Opportunity

        relationships = Relationship.get_relationships("contact", self.id, "opportunity")
        opp_ids = [rel.entity2_id if rel.entity1_type == "contact" else rel.entity1_id for rel in relationships]
        return Opportunity.query.filter(Opportunity.id.in_(opp_ids)).all()

    @property
    def managers(self):
        """
        Retrieve the managers for this Contact.
        Looks for relationships where this contact is the target (entity2)
        and the relationship_type is 'manager'.
        """
        rels = Relationship.query.filter_by(entity2_type="contact", entity2_id=self.id, relationship_type="manager").all()
        managers = []
        for rel in rels:
            if rel.entity1_type == "user":
                from app.models.user import User

                manager = User.query.get(rel.entity1_id)
            elif rel.entity1_type == "contact":
                manager = Contact.query.get(rel.entity1_id)
            if manager:
                managers.append(manager)
        return managers

    @property
    def direct_reports(self):
        """
        Retrieve contacts (or users) managed by this Contact.
        Looks for relationships where this contact is the source (entity1)
        and the relationship_type is 'manager'.
        """
        rels = Relationship.query.filter_by(entity1_type="contact", entity1_id=self.id, relationship_type="manager").all()
        subs = []
        for rel in rels:
            if rel.entity2_type == "contact":
                direct_report = Contact.query.get(rel.entity2_id)
            elif rel.entity2_type == "user":
                from app.models.user import User

                direct_report = User.query.get(rel.entity2_id)
            if direct_report:
                subs.append(direct_report)
        return subs

    def __repr__(self) -> str:
        return f"<Contact {self.id} {self.full_name}>"

    @direct_reports.setter
    def direct_reports(self, direct_report_list):
        """Set direct reports for this Contact by creating appropriate relationships."""
        # Ensure contact has ID
        if not self.id:
            db.session.add(self)
            db.session.flush()

        # Clear existing direct report relationships
        Relationship.query.filter_by(entity1_type="contact", entity1_id=self.id, relationship_type="manager").delete()

        # Add new direct report relationships
        if direct_report_list:
            for direct_report in direct_report_list:
                if isinstance(direct_report, dict):
                    report_type = direct_report.get("type", "contact")
                    report_id = direct_report.get("id")
                elif hasattr(direct_report, "id"):
                    report_type = direct_report.__class__.__name__.lower()
                    report_id = direct_report.id
                else:
                    report_type = "contact"
                    report_id = int(direct_report)

                relationship = Relationship(
                    entity1_type="contact",
                    entity1_id=self.id,
                    entity2_type=report_type,
                    entity2_id=report_id,
                    relationship_type="manager",
                )
                db.session.add(relationship)

    @managers.setter
    def managers(self, manager_list):
        """Set managers for this Contact by creating appropriate relationships."""
        # Ensure contact has ID
        if not self.id:
            db.session.add(self)
            db.session.flush()

        # Clear existing manager relationships
        Relationship.query.filter_by(entity2_type="contact", entity2_id=self.id, relationship_type="manager").delete()

        # Add new manager relationships
        if manager_list:
            for manager in manager_list:
                if isinstance(manager, dict):
                    manager_type = manager.get("type", "user")
                    manager_id = manager.get("id")
                elif hasattr(manager, "id"):
                    manager_type = manager.__class__.__name__.lower()
                    manager_id = manager.id
                else:
                    manager_type = "user"
                    manager_id = int(manager)

                relationship = Relationship(
                    entity1_type=manager_type,
                    entity1_id=manager_id,
                    entity2_type="contact",
                    entity2_id=self.id,
                    relationship_type="manager",
                )
                db.session.add(relationship)

    @opportunities.setter
    def opportunities(self, opportunity_list):
        """Set opportunities linked to this Contact by creating appropriate relationships."""
        # Ensure contact has ID
        if not self.id:
            db.session.add(self)
            db.session.flush()

        # Clear existing opportunity relationships for this contact
        Relationship.query.filter(
            ((Relationship.entity1_type == "contact") & (Relationship.entity1_id == self.id) & (Relationship.entity2_type == "opportunity"))
            | (
                (Relationship.entity2_type == "contact")
                & (Relationship.entity2_id == self.id)
                & (Relationship.entity1_type == "opportunity")
            )
        ).delete()

        # Add new opportunity relationships
        if opportunity_list:
            for opportunity in opportunity_list:
                if isinstance(opportunity, dict):
                    opp_id = opportunity.get("id")
                elif hasattr(opportunity, "id"):
                    opp_id = opportunity.id
                else:
                    opp_id = int(opportunity)

                relationship = Relationship(
                    entity1_type="contact", entity1_id=self.id, entity2_type="opportunity", entity2_id=opp_id, relationship_type="linked"
                )
                db.session.add(relationship)
