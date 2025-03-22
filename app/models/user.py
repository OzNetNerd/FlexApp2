from models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class User(db.Model, BaseModel):
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    notes = db.relationship('Note', backref='author', lazy='dynamic')

    __field_order__ = [
        {
            "name": "username",
            "label": "Username",
            "type": "text",
            "required": True,
            "section": "Basic Info"
        },
        {
            "name": "name",
            "label": "Name",
            "type": "text",
            "required": True,
            "section": "Basic Info"
        },
        {
            "name": "email",
            "label": "Email",
            "type": "email",
            "required": True,
            "section": "Contact"
        },
        {
            "name": "created_at",
            "label": "Created At",
            "type": "datetime",
            "readonly": True,
            "section": "Record Info"
        },
        {
            "name": "updated_at",
            "label": "Updated At",
            "type": "datetime",
            "readonly": True,
            "section": "Record Info"
        }
    ]

    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def search_by_username(query):
        """Search users by username for mentions."""
        logger.debug(f"Searching for users with username starting with '{query}'")
        result = User.query.filter(User.username.ilike(f'{query}%')).all()
        logger.debug(f"Found {len(result)} users matching the query '{query}'")
        return result