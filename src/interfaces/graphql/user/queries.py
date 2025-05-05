"""GraphQL queries for user operations."""

import strawberry
from typing import List, Optional
from src.application.user.queries import UserQueryHandler
from src.interfaces.graphql.user.types import User


@strawberry.type
class UserQueries:
    """GraphQL query resolvers for user operations."""

    def __init__(self, query_handler: UserQueryHandler):
        """Initialize with query handler."""
        self.query_handler = query_handler

    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """Get a user by ID."""
        user_dto = self.query_handler.get_user_by_id(id)
        return User.from_dto(user_dto) if user_dto else None

    @strawberry.field
    def users(self) -> List[User]:
        """Get all users."""
        user_dtos = self.query_handler.get_all_users()
        return [User.from_dto(dto) for dto in user_dtos]

    @strawberry.field
    def search_users(self, query: str) -> List[User]:
        """Search for users by username."""
        user_dtos = self.query_handler.search_users_by_username(query)
        return [User.from_dto(dto) for dto in user_dtos]