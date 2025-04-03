from typing import Union, Optional
import traceback
from flask import render_template, request, current_app
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
import logging
from app.routes.base.components.entity_handler import BasicContext, TableContext, ResourceContext

logger = logging.getLogger(__name__)

def render_safely(
        template_name: str,
        context: Union[BasicContext, TableContext, ResourceContext],
        fallback_error_message: str = "An error occurred while rendering the page",
        endpoint_name: Optional[str] = None,
) -> tuple[str, int] | str:
    """Safely renders a template with comprehensive error handling and logging.

    This function wraps Flask's render_template with error handling to prevent
    template errors from causing application crashes. It logs the rendering
    process, catches exceptions, and provides graceful degradation options.

    Args:
        template_name: Name of the template to render.
        context: Context object containing data to pass to the template.
        fallback_error_message: Generic error message to display when an error
            occurs and debug mode is off.
        endpoint_name: Optional endpoint name to use in logs. If None, tries to
            use request.endpoint.

    Returns:
        Either a rendered template string or a tuple of (error HTML, status code)
        in case of rendering failures.

    Raises:
        No exceptions are raised; all are caught and handled internally.
    """
    current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
    current_path = request.path

    try:
        logger.debug(f"🔍 Rendering template: {template_name} for {current_endpoint} ({current_path})")
        # Log the context being passed into the template to check for unexpected fields
        logger.debug(f"🔧 Context Data: {context}")

        # Log the successful pageview here
        logger.info(f"Pageview: Successfully rendered template: {template_name} for {current_endpoint} ({current_path})")
        return render_template(template_name, **context.__dict__)
    except (TemplateNotFound, TemplateSyntaxError, Exception) as e:
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

        logger.error(f"{error_type} in '{template_name}' for {current_endpoint} ({current_path}): {details}")

        # Log additional context data for error identification
        logger.debug(f"🔧 Error Context Data: {context}")

        if current_app.debug:
            logger.debug(f"Traceback:\n{traceback.format_exc()}")

        context.error_message = f"{error_type}: {details}" if current_app.debug else fallback_error_message

        try:
            logger.debug(f"🔁 Fallback render attempt for: {template_name}")
            return render_template(template_name, **context.__dict__), status_code
        except Exception as e2:
            logger.critical(f"Failed to re-render '{template_name}' with error context: {e2} for {current_endpoint} ({current_path})")
            return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code