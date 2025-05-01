import inspect
import logging
import time

from jinja2 import DebugUndefined

logger = logging.getLogger(__name__)

REQUEST_IDS = {}


def get_logger() -> logging.Logger:
    """Return a logger named for the calling module.

    Inspects the call stack to determine the module name of the caller
    and returns a logger instance with that name.

    Returns:
        Logger: A configured Python logger for the caller's module.
    """
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame)
    name = module.__name__ if module and hasattr(module, "__name__") else __name__
    return logging.getLogger(name)


def log_instance_vars(instance_details, instance, exclude: list[str] = None) -> None:
    exclude = exclude or []
    logger.info(f"📋 Attributes for {instance_details}: ")
    for attr, value in vars(instance).items():
        if attr in exclude:
            continue
        logger.info(f"  📝 {attr}: {value}")
    if exclude:
        logger.info(f"  ℹ️ (Excluded: {', '.join(exclude)})")
    else:
        logger.info("  ℹ️ (No exclusions)")


def log_message_and_variables(message: str, variables: dict) -> None:
    logger.info(message)
    for key, value in variables.items():
        logger.info(f"  📝 {key}: {value}")


class FunctionNameFilter(logging.Filter):
    def __init__(self, function_name):
        super().__init__()
        self.function_name = function_name

    def filter(self, record):
        record.funcName = self.function_name
        return True


def start_timer():
    return time.time()


def log_elapsed(timer_start, message):
    elapsed = time.time() - timer_start
    logger.debug(f"⏱️ {message}: {elapsed: .4f} seconds")


class LoggingUndefined(DebugUndefined):
    _missing_variables = set()

    def _log(self, msg: str):
        var_name = self._undefined_name
        self.__class__._missing_variables.add(var_name)
        logger.warning(f"⚠️  {msg}: {var_name!r}")

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
