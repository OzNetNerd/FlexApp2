from typing import Union, Optional
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
    it attempts to render a debug panel. If that also fails, it returns static HTML.

    Returns a tuple (HTML, status_code) on error, or a rendered string on success.
    """

    current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
    logger.info(f"🔍 Routing to endpoint: {current_endpoint}")

    log_title = f"🔍 Context vars in {template_name}:"
    kwargs = {
        "context": context,
        "fallback_error_message": fallback_error_message,
        "endpoint_name": endpoint_name,
    }
    log_kwargs(log_title=log_title, **context.__dict__, **kwargs)

    current_path = request.path

    template_env = Environment(
        loader=current_app.jinja_loader,
        undefined=LoggingUndefined,
    )

    flask_globals = {
        "url_for": url_for,
        "get_flashed_messages": get_flashed_messages,
        "request": request,
        "session": session,
    }

    try:
        logger.debug(f"🔍 Rendering template: {template_name} for {current_endpoint} ({current_path})")
        logger.debug(f"🔧 Context Data: {context}")
        template = template_env.get_template(template_name)
        return template.render(**flask_globals, **context.__dict__)

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
            error_type = "❌  Rendering error"
            details = str(e)
            status_code = 500

        logger.error(f"{error_type} in '{template_name}' for {current_endpoint} ({current_path}): {details}")
        logger.debug(f"🔧 Error Context Data: {context}")

        if current_app.debug:
            logger.debug(f"Traceback:\n{traceback.format_exc()}")

        context.error_message = f"{error_type}: {details}" if current_app.debug else fallback_error_message

        try:
            logger.debug(f"🔁 Fallback render attempt for: {template_name}")
            template = template_env.get_template(template_name)
            return template.render(**flask_globals, **context.__dict__), status_code

        except Exception as e2:
            logger.critical(f"❌  Failed to re-render '{template_name}' with error context: {e2} for {current_endpoint} ({current_path})")

            try:
                return (
                    render_template(
                        "base/core/_debug_panel.html",
                        template_name=template_name,
                        debug_title="Fatal Rendering Error",
                        debug_severity="error",
                        debug_context={
                            "original_error": str(e),
                            "render_fallback_error": str(e2),
                            "template_name": template_name,
                            "endpoint": current_endpoint,
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
