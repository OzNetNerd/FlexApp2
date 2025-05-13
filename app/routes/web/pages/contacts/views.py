from flask import request
from flask_login import login_required
from app.models.pages.contact import Contact
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.contacts import contacts_bp
import json
from datetime import datetime


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@contacts_bp.route("/records", methods=["GET"])
@login_required
def records():
    from app.services.contact import ContactService

    # Get data from service
    contact_service = ContactService()
    contacts = contact_service.get_filtered_contacts(request.args.to_dict())

    # Convert to dict format for table
    table_data = [contact.to_dict() for contact in contacts]

    # Properly serialize to JSON with datetime handling
    json_data = json.dumps(table_data, default=json_serial)

    # Create appropriate context for the records view
    context = TableContext(
        model_class=Contact,
        read_only=True,
        action="view",
        show_heading=True,
        table_data=json_data  # Now sending pre-serialized JSON string
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/contacts/records.html",
        context=context,
        error_message="An error occurred while rendering the contacts records page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)