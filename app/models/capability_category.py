from app.models.base import db, BaseModel

class CapabilityCategory(db.Model, BaseModel):
    """Represents a category used to group capabilities in the CRM.

    Categories help classify capabilities into logical buckets (e.g. Security, Data).

    Attributes:
        name (str): The display name of the category (must be unique).
        capabilities (list[Capability]): All capabilities under this category.
    """

    __tablename__ = "capability_categories"

    name = db.Column(db.String(100), nullable=False, unique=True)

    capabilities = db.relationship(
        "Capability", backref="category", lazy="dynamic"
    )

    def __repr__(self) -> str:
        """String representation for debugging purposes.

        Returns:
            str: A string showing the category name.
        """
        return f"<CapabilityCategory {self.name}>"
