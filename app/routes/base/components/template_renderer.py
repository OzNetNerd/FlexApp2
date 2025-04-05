from typing import Union, Optional, Tuple, Dict, Any
import traceback
import logging
from flask import (
    render_template,
    request,
    current_app,
    url_for,
    get_flashed_messages,
    session,
)
from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

from app.routes.base.components.entity_handler import Context, TableContext, ResourceContext
from app.utils.app_logging import log_kwargs, LoggingUndefined

logger = logging.getLogger(__name__)


def get_flask_globals() -> Dict[str, Any]:
    """
    Returns a dictionary of Flask global objects needed for template rendering.
    """
    return {
        "url_for": url_for,
        "get_flashed_messages": get_flashed_messages,
        "request": request,
        "session": session,
    }


def create_template_environment() -> Environment:
    """
    Creates and returns a configured Jinja2 Environment.
    """
    return Environment(
        loader=current_app.jinja_loader,
        undefined=LoggingUndefined,
    )


def log_render_attempt(template_name: str, endpoint_name: str,
                       context: Union[Context, TableContext, ResourceContext]) -> None:
    """
    Logs information about a template rendering attempt.
    """
    current_path = request.path
    logger.debug(f"🔍 Rendering template: {template_name} for {endpoint_name} ({current_path})")
    logger.debug(f"🔧 Context Data: {context}")


def handle_template_error(
        e: Exception,
        template_name: str,
        endpoint_name: str,
        fallback_error_message: str
) -> Tuple[str, int, str]:
    """
    Handles template rendering errors and returns appropriate error information.

    Returns:
        Tuple containing (error_type, status_code, error_details)
    """
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
        error_type = "❌  Rendering error"
        details = str(e)
        status_code = 500

    logger.debug(f"🔧 Error Context Data: {endpoint_name}")

    if current_app.debug:
        logger.debug(f"Traceback:\n{traceback.format_exc()}")

    error_message = f"{error_type}: {details}" if current_app.debug else fallback_error_message

    return error_type, status_code, error_message


def render_debug_panel(
        template_name: str,
        original_error: str,
        render_fallback_error: str,
        endpoint_name: str,
        status_code: int
) -> Tuple[str, int]:
    """
    Renders a debug panel with error information.
    """
    current_path = request.path

    try:
        return (
            render_template(
                "base/core/_debug_panel.html",
                template_name=template_name,
                debug_title="Fatal Rendering Error",
                debug_severity="error",
                debug_context={
                    "original_error": original_error,
                    "render_fallback_error": render_fallback_error,
                    "template_name": template_name,
                    "endpoint": endpoint_name,
                    "path": current_path,
                },
                debug_data=None,
                debug_id="fatal",
                debug_expanded=True,
                debug_show_toggle=False,
                debug_capture_console=False,
            ),
            status_code,
        )
    except Exception as e3:
        logger.critical(f"❌ Even the debug panel failed: {e3}")
        return f"<h1>{fallback_error_message}</h1><p>{error_type}</p>", status_code


def render_safely(
        template_name: str,
        context: Union[Context, TableContext, ResourceContext],
        fallback_error_message: str = "An error occurred while rendering the page",
        endpoint_name: Optional[str] = None,
) -> Union[Tuple[str, int], str]:
    """
    Safely renders a Jinja2 template with error handling, fallback rendering,
    and structured logging for debugging purposes.

    If the first attempt to render fails, it tries to inject an error message
    into the context and re-render the same template. If that fails too,
    it attempts to render a debug panel. If that also fails, it returns static HTML.

    Returns a tuple (HTML, status_code) on error, or a rendered string on success.
    """
    current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
    logger.info(f"🔍 Routing to endpoint: {current_endpoint}")
    logger.info(f"🔍 Using template: {template_name}")

    # Log context variables
    log_title = f"🔍 Passing the following context vars to the template:"
    kwargs = {
        "context": context,
        "fallback_error_message": fallback_error_message,
        "endpoint_name": endpoint_name,
    }
    log_kwargs(log_title=log_title, **context.__dict__, **kwargs)

    # Get environment and globals
    template_env = create_template_environment()
    flask_globals = get_flask_globals()

    # First render attempt
    try:
        log_render_attempt(template_name, current_endpoint, context)
        template = template_env.get_template(template_name)
        return template.render(**flask_globals, **context.__dict__)

    except Exception as e:
        # Handle the error
        error_type, status_code, error_message = handle_template_error(
            e, template_name, current_endpoint, fallback_error_message
        )

        # Add error message to context
        context.error_message = error_message

        # Fallback render attempt
        try:
            logger.debug(f"🔁 Fallback render attempt for: {template_name}")
            template = template_env.get_template(template_name)
            return template.render(**flask_globals, **context.__dict__), status_code

        except Exception as e2:
            # Final fallback - debug panel or static HTML
            return render_debug_panel(
                template_name=template_name,
                original_error=str(e),
                render_fallback_error=str(e2),
                endpoint_name=current_endpoint,
                status_code=status_code
            )