# app/routes/web/users.py
from app.models import User
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.services.user_service import UserService

users_config = BlueprintConfig(
    model_class=User,
    service=UserService(User)
)

users_bp = create_crud_blueprint(users_config)

