"""GraphQL mutations for user operations."""

import strawberry
from typing import Optional
from application.user.commands import UserCommandHandler
from application.user.dto import CreateUserDTO, UpdateUserDTO
from interfaces.graphql.user.types import User, CreateUserInput, UpdateUserInput


@strawberry.type
class UserMutations:
    """GraphQL mutation resolvers for user operations."""

    def __init__(self, command_handler: UserCommandHandler):
        """Initialize with command handler."""
        self.command_handler = command_handler

    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        """Create a new user."""
        dto = CreateUserDTO(
            username=input.username,
            name=input.name,
            email=input.email,
            password=input.password,
            is_admin=input.is_admin
        )
        result_dto = self.command_handler.create_user(dto)
        return User.from_dto(result_dto)

    @strawberry.mutation
    def update_user(self, id: int, input: UpdateUserInput) -> Optional[User]:
        """Update an existing user."""
        dto = UpdateUserDTO(
            username=input.username,
            name=input.name,
            email=input.email,
            password=input.password,
            is_admin=input.is_admin
        )
        result_dto = self.command_handler.update_user(id, dto)
        return User.from_dto(result_dto) if result_dto else None

    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        """Delete a user."""
        return self.command_handler.delete_user(id)