from typing import Union, Optional, Tuple, Dict, Any
import traceback
import logging
import json

from flask import (
    render_template,
    request,
    current_app,
    url_for,
    get_flashed_messages,
    session,
)
from jinja2 import Environment, DebugUndefined
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from markupsafe import Markup, escape

from app.routes.base.components.entity_handler import BaseContext
from app.utils.app_logging import log_kwargs

logger = logging.getLogger(__name__)


class LoggingUndefined(DebugUndefined):
    """Tracks and logs all missing variables used in templates."""

    _missing_variables = set()

    def _log(self, msg: str):
        var_name = self._undefined_name
        self.__class__._missing_variables.add(var_name)
        logger.warning(f"⚠️  {msg}: '{var_name}'")

    def __str__(self):
        self._log("Undefined variable rendered as string")
        return f"<<undefined:{self._undefined_name}>>"

    __repr__ = __str__
    __html__ = __str__

    def __getitem__(self, key):
        self._log(f"Attempted to access key '{key}' on undefined variable")
        return self.__class__(
            hint=self._undefined_hint,
            obj=self._undefined_obj,
            name=f"{self._undefined_name}[{key!r}]"
        )

    def __getattr__(self, attr):
        self._log(f"Attempted to access attribute '{attr}' on undefined variable")
        return self.__class__(
            hint=self._undefined_hint,
            obj=self._undefined_obj,
            name=f"{self._undefined_name}.{attr}"
        )

    @classmethod
    def clear_missing_variables(cls):
        cls._missing_variables.clear()

    @classmethod
    def raise_if_missing(cls):
        if cls._missing_variables:
            missing_list = "\n".join(f"- {v}" for v in sorted(cls._missing_variables))
            raise RuntimeError(f"❌ Missing template variables:\n{missing_list}")


def safe_json_default(obj):
    if isinstance(obj, DebugUndefined):  # Includes LoggingUndefined
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def htmlsafe_json_dumps(obj):
    return Markup(escape(json.dumps(obj, default=safe_json_default)))


def create_template_environment() -> Environment:
    env = Environment(
        loader=current_app.jinja_loader,
        undefined=LoggingUndefined,
    )
    env.filters["tojson"] = lambda value: htmlsafe_json_dumps(value)
    return env


def get_flask_globals() -> Dict[str, Any]:
    """
    Returns a dictionary of Flask global objects needed for template rendering.
    """
    logger.info("Fetching Flask global objects for template rendering")

    globals_dict = {
        "url_for": url_for,
        "get_flashed_messages": get_flashed_messages,
        "request": request,
        "session": session,
    }
    logger.info(f"Got them: {globals_dict}")
    return globals_dict


def handle_template_error(e: Exception, template_name: str, endpoint_name: str, fallback_error_message: str) -> Tuple[str, int]:
    """
    Handles template rendering errors and returns a debug panel response.
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
        error_type = "❌ Rendering Error"
        details = str(e)
        status_code = 500

    logger.debug(f"🔧 Error Context data: {endpoint_name}")

    render_fallback_error = traceback.format_exc() if current_app.debug else fallback_error_message

    return render_debug_panel(
        template_name=template_name,
        original_error=details,
        render_fallback_error=render_fallback_error,
        endpoint_name=endpoint_name,
        status_code=status_code,
    )


def render_debug_panel(
    template_name: str, original_error: str, render_fallback_error: str, endpoint_name: str, status_code: int
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
    context: Union[BaseContext],
    fallback_error_message: str = "An error occurred while rendering the page",
    endpoint_name: Optional[str] = None,
) -> Union[Tuple[str, int], str]:
    """
    Safely renders a Jinja2 template with error handling, fallback rendering,
    and structured logging for debugging purposes.

    Returns a tuple (HTML, status_code) on error, or a rendered string on success.
    """
    current_endpoint = endpoint_name or request.endpoint or "unknown endpoint"
    logger.info(f"🔍 Routing to endpoint: {current_endpoint}")
    logger.info(f"🔍 Using template: {template_name}")

    log_title = "🔍 Passing the following context vars to the template:"
    kwargs = {
        "context": context,
        "fallback_error_message": fallback_error_message,
        "endpoint_name": endpoint_name,
    }
    log_kwargs(log_title=log_title, **context.__dict__, **kwargs)

    template_env = create_template_environment()
    current_path = request.path

    logger.info(f"🔍 Attempting to render template '{template_name}' for {endpoint_name} ({current_path})")
    logger.debug(f"🔧 Context data: {context}")

    try:
        template = template_env.get_template(template_name)

        LoggingUndefined.clear_missing_variables()
        rendered = template.render(**get_flask_globals(), **context.__dict__)
        LoggingUndefined.raise_if_missing()

        return rendered

    except Exception as e:
        logger.exception(f"❌ Error rendering template '{template_name}' at endpoint '{endpoint_name}'")
        return handle_template_error(e, template_name, endpoint_name, fallback_error_message)
