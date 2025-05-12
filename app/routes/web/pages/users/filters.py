from flask import request
from flask_login import login_required
from app.services.user import UserService
from app.routes.web.pages.users import users_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

user_service = UserService()

@users_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_users():
    filters = {
        "is_admin": request.args.get("is_admin"),
        "period": request.args.get("period"),
        "activity": request.args.get("activity")
    }

    users = user_service.get_filtered_users(filters)

    context = WebContext(
        title="Filtered Users",
        read_only=True,
        users=users,
        filters=filters
    )

    config = RenderSafelyConfig(
        template_path="pages/users/filtered.html",
        context=context,
        error_message="An error occurred while rendering the filtered users page",
        endpoint_name=request.endpoint
    )

    return render_safely(config)