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
        user_dict = vars(input)
        user = user_service.create(user_dict)
        return User.from_model(user)

    @strawberry.mutation
    def update_user(self, id: int, input: UpdateUserInput) -> Optional[User]:
        user_dict = {k: v for k, v in vars(input).items() if v is not None}
        user = user_service.update(id, user_dict)
        if not user:
            return None
        return User.from_model(user)

    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        return user_service.delete(id)