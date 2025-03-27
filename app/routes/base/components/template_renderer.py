import logging
import traceback
from flask import render_template, current_app, request
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

logger = logging.getLogger(__name__)


def render_safely(
    template_name: str,
    context: dict,
    fallback_error_message: str = "An error occurred while rendering the page",
    endpoint_name: str = None,
):
    """
    Render a Jinja2 template with error handling and fallback logic.

    Args:
        template_name (str): The name of the template to render.
        context (dict): Context dictionary for the template.
        fallback_error_message (str): Message to display if rendering fails.
        endpoint_name (str, optional): The name of the endpoint for logging context.

    Returns:
        Response: A rendered HTML template or error fallback response.
    """
    try:
        return render_template(template_name, **context)
    except (TemplateNotFound, TemplateSyntaxError, Exception) as e:
        current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
        current_path = request.path

        if isinstance(e, TemplateNotFound):
            error_type = "Template Not Found"
            details = f"The template '{e.name}' could not be found."
            status_code = 404
        elif isinstance(e, TemplateSyntaxError):
            error_type = "Template Syntax Error"
            details = f"Syntax error in template '{template_name}': {str(e)}"
            status_code = 500
        else:
            error_type = "Rendering Error"
            details = str(e)
            status_code = 500

        logger.error(
            f"{__name__} - ERROR - {error_type} in '{template_name}' for {current_endpoint} ({current_path}): {details}"
        )
        if current_app.debug:
            logger.debug(f"Traceback: {traceback.format_exc()}")

        # ✅ Provide error_message consistently to the template
        context["error_message"] = f"{error_type}: {details}" if current_app.debug else fallback_error_message

        try:
            return render_template(template_name, **context), status_code
        except Exception as e2:
            logger.critical(f"{__name__} - CRITICAL - Failed to re-render '{template_name}' with error context: {e2}")
            return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code
