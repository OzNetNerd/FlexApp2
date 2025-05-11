from flask import request
from flask_login import login_required
from app.models.pages.user import User
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.users import users_bp

@users_bp.route("/records", methods=["GET"])
@login_required
def records():
    context = TableContext(
        model_class=User,
        read_only=True,
        action="view",
        show_heading=True
    )

    config = RenderSafelyConfig(
        template_path="pages/users/records.html",
        context=context,
        error_message="An error occurred while rendering the users records page",
        endpoint_name=request.endpoint
    )

    return render_safely(config)