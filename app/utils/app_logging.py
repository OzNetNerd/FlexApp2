from jinja2 import DebugUndefined
import logging
import inspect

logger = logging.getLogger(__name__)


def configure_logging(level=logging.INFO) -> None:
    """Sets up basic logging configuration."""

    # Define a custom log format that includes the module and function names
    log_format = "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s"

    logging.basicConfig(
        level=level,
        format=log_format,
    )
    logger.info("✅ Logging is configured.")


def log_instance_vars(instance, exclude: list[str] = None) -> None:
    """Logs all instance variables of a class.

    Args:
        instance: The class instance.
        exclude: List of variable names to exclude from logging.
    """
    exclude = exclude or []
    logger.info(f"📋 Attributes for {instance.__class__.__name__}:")

    for attr, value in vars(instance).items():
        if attr in exclude:
            continue
        logger.info(f"  📝 {attr}: {value}")

    if exclude:
        logger.info(f"  ℹ️ (Excluded: {', '.join(exclude)})")
    else:
        logger.info("  ℹ️ (No exclusions)")


class FunctionNameFilter(logging.Filter):
    """A filter that changes the function name in log records."""

    def __init__(self, function_name):
        super().__init__()
        self.function_name = function_name

    def filter(self, record):
        # Modify the record's funcName attribute
        record.funcName = self.function_name
        return True  # Always include the record


def log_kwargs(log_title: str, **kwargs: dict) -> None:
    """Logs all keyword arguments with a title and a warning icon for empty values.
    Uses the caller's module and function name for the log.
    """
    # Get the caller's frame, module name, and function name
    caller_frame = inspect.currentframe().f_back
    caller_module = caller_frame.f_globals["__name__"]
    caller_function = caller_frame.f_code.co_name

    # Get a logger for the caller's module
    caller_logger = logging.getLogger(caller_module)

    # Create a filter with the caller's function name
    function_filter = FunctionNameFilter(caller_function)

    try:
        # Add the filter
        caller_logger.addFilter(function_filter)

        # Log messages with the filter applied
        caller_logger.info(f"{log_title}")

        for key, value in kwargs.items():
            is_empty = not value and value is not False
            # Only use ❓ for extra, otherwise use ⚠️ for empty values
            icon = "⚠️" if is_empty and key != "extra" else "📝"

            # Use ❓ specifically for empty "extra" field
            if is_empty and key == "extra":
                icon = "❓"

            if isinstance(value, dict):
                caller_logger.info(f"  {icon} {key}:")
                for subkey, sub_value in value.items():
                    sub_is_empty = not sub_value and sub_value is not False
                    sub_icon = "⚠️" if sub_is_empty else "📝"
                    caller_logger.info(f"    {sub_icon} {subkey}: {sub_value!r}")
            else:
                caller_logger.info(f"  {icon} {key}: {value!r}")

    finally:
        # Always remove the filter when done
        caller_logger.removeFilter(function_filter)


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
