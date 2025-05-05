# app/graphql/resolvers/user.py
import strawberry
from typing import List, Optional
from app.models.pages.user import User as UserModel
from app.services.user_service import UserService
from app.graphql.types.user import User

user_service = UserService(UserModel)


@strawberry.input
class CreateUserInput:
    username: str
    name: str
    email: str
    password: str
    is_admin: Optional[bool] = False


@strawberry.input
class UpdateUserInput:
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


@strawberry.type
class UserQueries:
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        user = user_service.get_by_id(id)
        if not user:
            return None
        return User.from_model(user)

    @strawberry.field
    def users(self) -> List[User]:
        return [User.from_model(user) for user in user_service.get_all()]

    @strawberry.field
    def search_users(self, query: str) -> List[User]:
        users = UserModel.search_by_username(query)
        return [User.from_model(user) for user in users]


@strawberry.type
class UserMutations:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        # Convert input to dict
        data = {
            "username": input.username,
            "name": input.name,
            "email": input.email,
            "password": input.password,
            "is_admin": input.is_admin,
        }

        # Validate
        errors = user_service.validate_create(data)
        if errors:
            raise ValueError(", ".join(errors))

        # Create user
        user = user_service.create(data)
        return User.from_model(user)

    @strawberry.mutation
    def update_user(self, id: int, input: UpdateUserInput) -> Optional[User]:
        # Get user
        user = user_service.get_by_id(id)
        if not user:
            return None

        # Convert input to dict, filtering out None values
        data = {k: v for k, v in vars(input).items() if v is not None}

        # Validate
        errors = user_service.validate_update(user, data)
        if errors:
            raise ValueError(", ".join(errors))

        # Update
        user = user_service.update(id, data)
        return User.from_model(user)

    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        user = user_service.get_by_id(id)
        if not user:
            return False
        return user_service.delete(id)
