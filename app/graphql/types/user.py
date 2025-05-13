# # app/graphql/types/user.py
# import strawberry
# from typing import Optional, List
# from app.models.pages.user import User as UserModel
#
#
# @strawberry.type
# class User:
#     id: int
#     username: str
#     name: str
#     email: str
#     is_admin: bool
#     created_at: str
#     updated_at: Optional[str]
#     related_users: Optional[str]
#     related_companies: Optional[str]
#
#     @classmethod
#     def from_model(cls, model: UserModel) -> "User":
#         return cls(
#             id=model.id,
#             username=model.username,
#             name=model.name,
#             email=model.email,
#             is_admin=model.is_admin,
#             created_at=str(model.created_at),
#             updated_at=str(model.updated_at) if model.updated_at else None,
#             related_users=model.to_dict().get("related_users", ""),
#             related_companies=model.to_dict().get("related_companies", "")
#         )
