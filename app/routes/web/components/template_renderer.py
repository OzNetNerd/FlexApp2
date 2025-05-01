# template_renderer.py

import inspect
import json
import traceback
from dataclasses import dataclass
from typing import Optional, Tuple, Union

from flask import abort, current_app, get_flashed_messages, render_template, request, url_for
from jinja2 import DebugUndefined, Environment
from jinja2.exceptions import TemplateNotFound
from markupsafe import Markup, escape

from app.routes.web.context import WebContext
from app.utils.app_logging import get_logger, log_message_and_variables

logger = get_logger()


@dataclass
class RenderSafelyConfig:
    template_path: str
    error_message: str
    endpoint_name: str
    context: Optional[WebContext] = None


class LoggingUndefined(DebugUndefined):
    """Tracks and logs all missing variables used in templates."""

    _missing_variables = set()

    def _log(self, msg: str):
        var_name = self._undefined_name
        frame = inspect.stack()[2]
        logger.warning(f"⚠️  {msg}: {var_name!r} (template file: {frame.filename}, line: {frame.lineno})")
        self.__class__._missing_variables.add(var_name)

    def __str__(self):
        self._log("Undefined variable rendered as string")
        return f"<<undefined: {self._undefined_name}>>"

    __repr__ = __str__
    __html__ = __str__

    def __getitem__(self, key):
        self._log(f"Attempted to access key {key!r} on undefined variable")
        return self.__class__(hint=self._undefined_hint, obj=self._undefined_obj, name=f"{self._undefined_name}[{key!r}]")

    def __getattr__(self, attr):
        self._log(f"Attempted to access attribute {attr!r} on undefined variable")
        return self.__class__(hint=self._undefined_hint, obj=self._undefined_obj, name=f"{self._undefined_name}.{attr}")

    @classmethod
    def clear_missing_variables(cls):
        cls._missing_variables.clear()

    @classmethod
    def raise_if_missing(cls):
        if cls._missing_variables:
            missing_list = "\n".join(f"- {v}" for v in sorted(cls._missing_variables))
            raise RuntimeError(f"❌ Missing template variables: \n{missing_list}")


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
    logger.debug(f"🔧 Created template environment with loader {current_app.jinja_loader}")
    return env


def get_jinja_variables(context_dict):
    # Start with context dictionary
    jinja_variables = context_dict.copy()

    # Define Flask globals dictionary
    flask_globals = {
        "url_for": url_for,
        "get_flashed_messages": get_flashed_messages,
        "request": request,
        "session": request.environ.get("flask.session"),
        "current_app": current_app,
    }

    # Add Flask globals, logging any overrides
    for key, flask_value in flask_globals.items():
        if key in jinja_variables:
            context_value = jinja_variables[key]
            logger.warning(f"⚠️ CONFLICT: '{key}' from context ({context_value}) overridden by Flask global ({flask_value})")
        jinja_variables[key] = flask_value

    # Log all variables being returned
    log_message_and_variables("Jinja variables:", jinja_variables)

    return jinja_variables


def handle_template_error(
    e: Exception,
    template_name: str,
    endpoint_name: str,
    fallback_error_message: str,
) -> tuple[str, int]:
    if isinstance(e, TemplateNotFound):
        abort(404)

    if hasattr(e, "lineno"):
        status_code = 500
        details = f"Syntax error in template {template_name!r}: {e}"
    else:
        status_code = 500
        details = str(e)

    error_body = traceback.format_exc() if current_app.debug else fallback_error_message

    return (
        render_template(
            "pages/errors/500.html",
            error_type="Rendering Error",
            details=details,
            error_body=error_body,
            endpoint=endpoint_name,
            path=request.path,
        ),
        status_code,
    )


def render_debug_panel(
    template_name: str,
    original_error: str,
    render_fallback_error: str,
    endpoint_name: str,
    status_code: int,
) -> Tuple[str, int]:
    current_path = request.path
    logger.info(f"🛠️ Rendering debug panel for template {template_name!r} at path {current_path!r}")

    try:
        html_response = render_template(
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
        )
        logger.info(f"Debug panel rendered successfully with status code {status_code}")
        logger.debug(f"📝 Response length: {len(html_response)} chars")
        return html_response, status_code
    except Exception as e3:
        logger.critical(f"❌ Even the debug panel failed: {e3}")
        logger.critical(f"❌ Debug panel error traceback: \n{traceback.format_exc()}")
        return f"<h1>Debug panel rendering failed</h1><p>{escape(original_error)}</p>", status_code


def render_safely(render_safely_config: RenderSafelyConfig) -> Union[Tuple[str, int], str]:
    """Render a Jinja template safely using Flask's built-in Jinja environment.

    Args:
        render_safely_config: Configuration holding endpoint name, template path, context, etc.

    Returns:
        The rendered template string, or an error tuple (body, status_code).
    """
    current_endpoint = render_safely_config.endpoint_name or request.endpoint or "unknown endpoint"
    current_path = request.path

    # Log request information
    logger.info(f"🔍 Routing to endpoint: {current_endpoint}")
    logger.info(f"🔍 Using template: {render_safely_config.template_path!r}")
    logger.debug(f"📝 Request ID: {id(request)}")
    logger.debug(f"📝 Request method: {request.method}")
    logger.debug(f"📝 Request path: {request.path}")
    logger.debug(f"📝 Request args: {request.args}")
    logger.debug(f"📝 Request headers: {dict(request.headers)}")
    logger.info(
        f"🔍 Attempting to render template {render_safely_config.template_path!r} for "
        f"{render_safely_config.endpoint_name!r} ({current_path!r})"
    )
    logger.debug(f"🔧 Context data: {render_safely_config.context}")

    # Prepare context dictionary
    try:
        context_dict = {} if render_safely_config.context is None else render_safely_config.context.to_dict()
    except ValueError as ve:
        logger.error(f"❌ Error converting context to dictionary: {ve}")
        return handle_template_error(
            ve,
            render_safely_config.template_path,
            render_safely_config.endpoint_name,
            f"Error preparing data: {ve}",
        )

    # Use Flask's pre-configured environment and render template
    try:
        template_env = current_app.jinja_env
        template = template_env.get_template(render_safely_config.template_path)
        logger.debug(f"Template {render_safely_config.template_path!r} loaded successfully")

        LoggingUndefined.clear_missing_variables()
        logger.debug("📝 Starting template rendering process")
        rendered = template.render(**get_jinja_variables(context_dict))
        logger.debug(f"Template rendered successfully with length {len(rendered)} chars")

        LoggingUndefined.raise_if_missing()
        logger.info(f"Template {render_safely_config.template_path!r} rendered successfully")
        logger.debug(f"📝 Response content length: {len(rendered)} chars")

        return rendered

    except Exception as e:
        logger.exception(
            f"❌ Error rendering template {render_safely_config.template_path!r} "
            f"at endpoint {render_safely_config.endpoint_name!r}"
        )
        logger.error(f"❌ Exception details: {type(e).__name__}: {e}")
        return handle_template_error(
            e,
            render_safely_config.template_path,
            render_safely_config.endpoint_name,
            render_safely_config.error_message,
        )