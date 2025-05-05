"""Safe template rendering with error handling and debugging.

This module provides utilities for safely rendering Jinja templates
with robust error handling, debugging, and logging capabilities.
"""

import inspect
import json
import traceback
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from flask import abort, current_app, get_flashed_messages, render_template, request, url_for
from jinja2 import DebugUndefined, Environment
from jinja2.exceptions import TemplateNotFound
from markupsafe import Markup, escape

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RenderSafelyConfig:
    """Configuration for safe template rendering.

    Attributes:
        template_path: Path to the template file.
        context: Context object containing variables for the template.
        error_message: Message to display if rendering fails.
        endpoint_name: Name of the endpoint being rendered.
    """
    template_path: str
    context: Any  # BaseContext
    error_message: str
    endpoint_name: str


class LoggingUndefined(DebugUndefined):
    """Tracks and logs all missing variables used in templates.

    Extends Jinja's DebugUndefined to provide detailed logging when
    undefined variables are accessed in templates.
    """
    _missing_variables = set()

    def _log(self, msg: str) -> None:
        """Log a message about an undefined variable.

        Args:
            msg: Message describing the undefined access.
        """
        var_name = self._undefined_name
        frame = inspect.stack()[2]
        logger.warning(f"⚠️  {msg}: {var_name!r} (template file: {frame.filename}, line: {frame.lineno})")
        self.__class__._missing_variables.add(var_name)

    def __str__(self) -> str:
        """Convert to string representation."""
        self._log("Undefined variable rendered as string")
        return f"<<undefined: {self._undefined_name}>>"

    __repr__ = __str__
    __html__ = __str__

    def __getitem__(self, key):
        """Handle attempts to access items on undefined variables."""
        self._log(f"Attempted to access key {key!r} on undefined variable")
        return self.__class__(hint=self._undefined_hint, obj=self._undefined_obj,
                              name=f"{self._undefined_name}[{key!r}]")

    def __getattr__(self, attr):
        """Handle attempts to access attributes on undefined variables."""
        self._log(f"Attempted to access attribute {attr!r} on undefined variable")
        return self.__class__(hint=self._undefined_hint, obj=self._undefined_obj, name=f"{self._undefined_name}.{attr}")

    @classmethod
    def clear_missing_variables(cls) -> None:
        """Clear the set of tracked missing variables."""
        cls._missing_variables.clear()

    @classmethod
    def raise_if_missing(cls) -> None:
        """Raise an exception if any undefined variables were accessed."""
        if cls._missing_variables:
            missing_list = "\n".join(f"- {v}" for v in sorted(cls._missing_variables))
            raise RuntimeError(f"❌ Missing template variables: \n{missing_list}")


def render_safely(config: RenderSafelyConfig) -> Union[str, Tuple[str, int]]:
    """Render a Jinja template safely with error handling.

    Args:
        config: Configuration for template rendering.

    Returns:
        The rendered template string, or an error response tuple.
    """
    current_endpoint = config.endpoint_name or request.endpoint or "unknown endpoint"
    logger.info(f"🔍 Routing to endpoint: {current_endpoint}")
    logger.info(f"🔍 Using template: {config.template_path!r}")

    # Get Flask's pre-configured Jinja environment
    template_env = current_app.jinja_env

    try:
        try:
            context_dict = config.context.to_dict()
        except ValueError as ve:
            logger.error(f"❌ Error converting context to dictionary: {ve}")
            return handle_template_error(
                ve, config.template_path, config.endpoint_name, f"Error preparing data: {ve}"
            )

        template = template_env.get_template(config.template_path)
        LoggingUndefined.clear_missing_variables()

        jinja_variables = _get_jinja_variables(context_dict)
        rendered = template.render(**jinja_variables)

        # Optionally raise if missing variables were detected
        LoggingUndefined.raise_if_missing()
        logger.info(f"Template {config.template_path!r} rendered successfully")

        return rendered

    except Exception as e:
        logger.exception(
            f"❌ Error rendering template {config.template_path!r} at endpoint {config.endpoint_name!r}"
        )
        return handle_template_error(
            e, config.template_path, config.endpoint_name, config.error_message
        )


def _get_jinja_variables(context_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Get all variables to be passed to the Jinja template.

    Args:
        context_dict: Base context dictionary.

    Returns:
        Complete dictionary of variables for the template.
    """
    # Implementation details...
    # (I'm omitting the full implementation for brevity)
    return context_dict


def handle_template_error(
        e: Exception, template_name: str, endpoint_name: str, fallback_error_message: str
) -> Tuple[str, int]:
    """Handle exceptions during template rendering.

    Args:
        e: The exception that occurred.
        template_name: Name of the template that failed.
        endpoint_name: Name of the endpoint being rendered.
        fallback_error_message: Message to display if rendering fails.

    Returns:
        Error response tuple (content, status_code).
    """
    # Implementation details...
    # (I'm omitting the full implementation for brevity)
    return render_template("pages/errors/500.html"), 500