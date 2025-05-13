# # app/graphql/dataloaders/loaders.py
# import strawberry
# from typing import List, Dict, Optional
# from app.models.pages.user import User as UserModel
#
# class UserLoader:
#     async def load_users(self, keys: List[int]) -> List[Optional[UserModel]]:
#         users_by_id = {user.id: user for user in UserModel.query.filter(UserModel.id.in_(keys)).all()}
#         return [users_by_id.get(key) for key in keys]
#
# # Initialize in your app context
# user_loader = UserLoader()
