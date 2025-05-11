from flask import request
from flask_login import login_required
from app.services.user_service import UserService
from app.routes.web.pages.users import users_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

user_service = UserService()

@users_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def users_dashboard():
    stats = user_service.get_dashboard_stats()
    user_categories = user_service.get_user_categories()
    top_users = user_service.get_top_users(5)
    activity_data = user_service.prepare_activity_data()

    context = WebContext(
        title="Users Dashboard",
        read_only=True,
        stats=stats,
        user_categories=user_categories,
        top_users=top_users,
        activity_data=activity_data
    )

    config = RenderSafelyConfig(
        template_path="pages/users/dashboard.html",
        context=context,
        error_message="An error occurred while rendering the users dashboard",
        endpoint_name=request.endpoint
    )

    return render_safely(config)