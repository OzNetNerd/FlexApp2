import logging
import traceback
from flask import render_template, current_app, request
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

logger = logging.getLogger(__name__)


def render_safely(template_name, context, fallback_error_message="An error occurred while rendering the page",
                  endpoint_name=None):
    """
    Render template with improved error handling.

    Args:
        template_name: Name of the template to render
        context: Dictionary of variables to pass to the template
        fallback_error_message: User-friendly message to display on error

    Returns:
        Rendered template or error page with appropriate status code
    """
    try:
        response = render_template(template_name, **context)
        return response
    except TemplateNotFound as e:
        # Handle missing template specifically
        error_type = "Template Not Found"
        details = f"The template '{e.name}' could not be found."
        status_code = 404

        # Get endpoint info for better context
        current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
        current_path = request.path

        logger.error(
            f"{__name__} - ERROR - Template not found: {e.name} while rendering {current_endpoint} (URL: {current_path})")
    except TemplateSyntaxError as e:
        # Handle template syntax errors
        error_type = "Template Syntax Error"
        details = f"Syntax error in template '{template_name}': {str(e)}"
        status_code = 500

        # Get endpoint info for better context
        current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
        current_path = request.path

        logger.error(
            f"{__name__} - ERROR - Template syntax error in '{template_name}' while rendering {current_endpoint} (URL: {current_path}): {str(e)}")
    except Exception as e:
        # Handle all other exceptions
        error_type = "Rendering Error"
        details = str(e)
        status_code = 500

        # Get endpoint info for better context
        current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
        current_path = request.path

        # Log the full traceback for debugging but don't expose it to users
        logger.error(
            f"{__name__} - ERROR - Failed to render '{template_name}' for {current_endpoint} (URL: {current_path}): {str(e)}")
        if current_app.debug:
            logger.debug(f"Traceback: {traceback.format_exc()}")

    try:
        # Attempt to render the error template
        current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
        current_path = request.path

        return render_template(
            "errors/500.html",
            error_message=fallback_error_message,
            error_type=error_type,
            error_details=details if current_app.debug else None,
            endpoint=current_endpoint,
            path=current_path
        ), status_code
    except Exception:
        # If error template fails, return a basic HTTP response
        logger.critical("Error template failed to render, returning basic response")
        return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code