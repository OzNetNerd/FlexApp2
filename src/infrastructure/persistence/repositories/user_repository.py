"""SQLAlchemy implementation of the UserRepository interface."""

from typing import Optional, List
from domain.user.entities import User as UserEntity
from domain.user.repositories import UserRepository
from infrastructure.persistence.models.user import User as UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def get_by_id(self, id: int) -> Optional[UserEntity]:
        """Get user by ID."""
        model = UserModel.query.get(id)
        return self._to_entity(model) if model else None

    def get_all(self) -> List[UserEntity]:
        """Get all users."""
        models = UserModel.query.all()
        return [self._to_entity(model) for model in models]

    def add(self, user: UserEntity) -> UserEntity:
        """Add a new user."""
        model = UserModel(
            username=user.username,
            name=user.name,
            email=user.email,
            is_admin=user.is_admin
        )
        model.save()
        return self._to_entity(model)

    def update(self, user: UserEntity) -> UserEntity:
        """Update an existing user."""
        model = UserModel.query.get(user.id)
        if not model:
            raise ValueError(f"User with ID {user.id} not found")

        model.username = user.username
        model.name = user.name
        model.email = user.email
        model.is_admin = user.is_admin
        model.save()
        return self._to_entity(model)

    def delete(self, id: int) -> bool:
        """Delete a user."""
        model = UserModel.query.get(id)
        if model:
            model.delete()
            return True
        return False

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """Get user by username."""
        model = UserModel.query.filter_by(username=username).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Get user by email."""
        model = UserModel.query.filter_by(email=email).first()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: UserModel) -> UserEntity:
        """
        Convert model to domain entity.

        Args:
            model: Database model to convert

        Returns:
            Domain entity representation
        """
        return UserEntity(
            id=model.id,
            username=model.username,
            name=model.name,
            email=model.email,
            is_admin=model.is_admin,
            created_at=str(model.created_at),
            updated_at=str(model.updated_at) if model.updated_at else None,
            related_users=model.to_dict().get("related_users", ""),
            related_companies=model.to_dict().get("related_companies", "")
        )