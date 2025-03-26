from app.models.base import db, BaseModel
from app.models.company_capability import CompanyCapability


class Capability(BaseModel):
    """Represents a capability offered by companies in the CRM.

    Used to categorize what a company can do, linked through
    CompanyCapability associations.

    Attributes:
        name (str): Name of the capability.
        category_id (int): Foreign key linking to a capability category.
        company_capabilities (list[CompanyCapability]): Associations to companies.
    """

    __tablename__ = "capabilities"

    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("capability_categories.id"), nullable=False
    )

    company_capabilities = db.relationship(
        "CompanyCapability",
        back_populates="capability",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def companies(self) -> list:
        """Return all Company objects that use this capability.

        Returns:
            list: Companies associated with this capability via CompanyCapability.
        """
        return [cc.company for cc in self.company_capabilities]

    def __repr__(self) -> str:
        """String representation for debugging purposes.

        Returns:
            str: A string showing the capability's name.
        """
        return f"<Capability {self.name}>"
