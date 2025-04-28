# app/routes/web/users.py
from app.models import User
from app.routes.web.blueprint_factory import create_crud_blueprint
from app.services.user_service import UserService

users_bp = create_crud_blueprint(User, service=UserService(User))