from flask import request
from flask_login import login_required
from app.models.pages.user import User
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.users import users_bp
import json
from datetime import datetime


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@users_bp.route("/records", methods=["GET"])
@login_required
def records():
    from app.services.user import UserService

    # Get data from service
    user_service = UserService()
    users = user_service.get_filtered_users(request.args.to_dict())

    # Convert to dict format for table
    table_data = [user.to_dict() for user in users]

    # Properly serialize to JSON with datetime handling
    json_data = json.dumps(table_data, default=json_serial)

    # Create appropriate context for the records view
    context = TableContext(
        model_class=User,
        read_only=True,
        action="view",
        show_heading=True,
        table_data=json_data  # Now sending pre-serialized JSON string
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/users/records.html",
        context=context,
        error_message="An error occurred while rendering the users records page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)