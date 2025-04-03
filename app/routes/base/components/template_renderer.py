from typing import Union, Optional
import traceback
from flask import render_template, request, current_app
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
import logging
from app.routes.base.components.entity_handler import Context, TableContext, ResourceContext

logger = logging.getLogger(__name__)

def render_safely(
        template_name: str,
        context: Union[Context, TableContext, ResourceContext],
        fallback_error_message: str = "An error occurred while rendering the page",
        endpoint_name: Optional[str] = None,
) -> tuple[str, int] | str:
    """
    Safely renders a Jinja2 template with error handling, fallback rendering,
    and structured logging for debugging purposes.

    If the first attempt to render fails, it tries to inject an error message
    into the context and re-render the same template. If that fails too,
    it returns a static error message as a last resort.

    Returns a tuple (HTML, status_code) on error, or a rendered string on success.
    """

    # Determine which endpoint and path this render attempt is for (used in logging).
    current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
    current_path = request.path

    try:
        # Log the intent to render a template with the specified context.
        logger.debug(f"🔍 Rendering template: {template_name} for {current_endpoint} ({current_path})")
        logger.debug(f"🔧 Context Data: {context}")

        # Attempt to render the template. If successful, return the HTML.
        return render_template(template_name, **context.__dict__)

    except (TemplateNotFound, TemplateSyntaxError, Exception) as e:
        # Template could not be rendered — categorize the error and prepare a fallback.

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

        # Log the error type and details for observability and debugging.
        logger.error(f"{error_type} in '{template_name}' for {current_endpoint} ({current_path}): {details}")
        logger.debug(f"🔧 Error Context Data: {context}")

        if current_app.debug:
            # In debug mode, also log the full traceback for troubleshooting.
            logger.debug(f"Traceback:\n{traceback.format_exc()}")

        # Store the error message in the context for the fallback render attempt.
        # In debug mode: include detailed error info. Otherwise: show friendly error message.
        context.error_message = f"{error_type}: {details}" if current_app.debug else fallback_error_message

        try:
            # 🔁 HERE is where the "re-render" occurs:
            # A second attempt to render the *same* template, this time with the updated context
            # that now includes `error_message`. This is done to show the user an error message
            # within the same page layout if the original render fails.
            logger.debug(f"🔁 Fallback render attempt for: {template_name}")
            return render_template(template_name, **context.__dict__), status_code

        except Exception as e2:
            # Even the fallback render failed — this is the last resort.
            # Return a minimal HTML error message directly.
            logger.critical(f"Failed to re-render '{template_name}' with error context: {e2} for {current_endpoint} ({current_path})")
            return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code
