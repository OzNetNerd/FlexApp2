from flask import request
from flask_login import login_required
from app.services.user import UserService
from app.routes.web.pages.users import users_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

user_service = UserService()

@users_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    stats = user_service.get_statistics()

    context = WebContext(
        title="User Statistics",
        read_only=True,
        total_users=stats["total_users"],
        regular_users=stats["regular_users"],
        admin_users=stats["admin_users"],
        inactive_users=stats["inactive_users"],
        avg_activity_per_user=stats["avg_activity_per_user"],
        user_activity_by_role=stats["user_activity_by_role"],
        monthly_data=stats["monthly_data"]
    )

    config = RenderSafelyConfig(
        template_path="pages/users/statistics.html",
        context=context,
        error_message="An error occurred while rendering the user statistics page",
        endpoint_name=request.endpoint
    )

    return render_safely(config)