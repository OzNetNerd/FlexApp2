import logging
import traceback
from flask import render_template, current_app, request
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

logger = logging.getLogger(__name__)


def render_safely(
    template_name,
    context,
    fallback_error_message="An error occurred while rendering the page",
    endpoint_name=None,
):
    """
    Render template with improved error handling and toast fallback.

    Args:
        template_name: Name of the template to render
        context: Dictionary of variables to pass to the template
        fallback_error_message: User-friendly message to display on error
        endpoint_name: Optional endpoint name for logging

    Returns:
        Rendered template with error toast or fallback HTML
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

        # Add error message to context
        context["template_render_error"] = (
            f"{error_type}: {details}" if current_app.debug else fallback_error_message
        )

        try:
            # ✅ Retry rendering the *same* template with toast message injected
            return render_template(template_name, **context), status_code
        except Exception as e2:
            logger.critical(
                f"{__name__} - CRITICAL - Failed to re-render '{template_name}' with error context: {e2}"
            )
            return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code
