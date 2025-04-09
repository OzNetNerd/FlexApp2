import logging
import inspect
import time
import uuid
import re
import sys
from jinja2 import DebugUndefined

logger = logging.getLogger("app")

REQUEST_IDS = {}


# def configure_logging(level=logging.INFO) -> logging.Logger:
#     """Sets up and returns a custom logger with filters and console output."""
#     logger.setLevel(level)
#
#     if not logger.handlers:
#         handler = logging.StreamHandler(sys.stdout)
#         formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s")
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#
#     # Add filters
#     logger.addFilter(RequestIDFilter())
#     logger.addFilter(EmojiLogFilter())
#     logger.propagate = False
#
#     logger.info("✅ Logging is configured.")
#     return logger
#
#
# class RequestIDFilter(logging.Filter):
#     """Filter that adds request ID and Flask request context to log records."""
#
#     def filter(self, record):
#         try:
#             from flask import request, has_request_context
#
#             if has_request_context():
#                 if id(request) not in REQUEST_IDS:
#                     REQUEST_IDS[id(request)] = str(uuid.uuid4())[:8]
#                 record.request_id = REQUEST_IDS[id(request)]
#                 record.request_method = request.method
#                 record.request_path = request.path
#                 record.msg = f"[{record.request_id}] {record.msg}"
#             else:
#                 record.request_id = "-"
#         except Exception:
#             record.request_id = "-"
#         return True
#
#
# class EmojiLogFilter(logging.Filter):
#     """Adds emojis based on known message patterns."""
#
#     def filter(self, record):
#         if record.msg and isinstance(record.msg, str):
#             if re.match(r"^\s*[^\w\s]", record.msg):
#                 return True
#
#             msg = record.msg.strip()
#
#             if msg.startswith("Registering"):
#                 record.msg = f"🔧 {record.msg}"
#             elif msg.startswith("Registered"):
#                 record.msg = f"✅ {record.msg}"
#             elif msg.startswith("Successfully"):
#                 record.msg = f"✅ {record.msg}"
#             elif msg.startswith("Set"):
#                 record.msg = f"🔠 {record.msg}"
#             elif msg.startswith("Initializing"):
#                 record.msg = f"🔧 {record.msg}"
#             elif msg.startswith("Web Request"):
#                 record.msg = f"📥 {record.msg}"
#
#         return True


def log_instance_vars(instance_details, instance, exclude: list[str] = None) -> None:
    exclude = exclude or []
    logger.info(f"📋 Attributes for {instance_details}:")
    for attr, value in vars(instance).items():
        if attr in exclude:
            continue
        logger.info(f"  📝 {attr}: {value}")
    if exclude:
        logger.info(f"  ℹ️ (Excluded: {', '.join(exclude)})")
    else:
        logger.info("  ℹ️ (No exclusions)")


def log_message_and_vars(message: str, vars: dict) -> None:
    # Log the provided message
    logger.info(message)

    # Log each variable with indentation
    for key, value in vars.items():
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
    logger.debug(f"⏱️ {message}: {elapsed:.4f} seconds")


class LoggingUndefined(DebugUndefined):
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
        return self.__class__(hint=self._undefined_hint, obj=self._undefined_obj, name=f"{self._undefined_name}[{key!r}]")

    def __getattr__(self, attr):
        self._log(f"Attempted to access attribute '{attr}' on undefined variable")
        return self.__class__(hint=self._undefined_hint, obj=self._undefined_obj, name=f"{self._undefined_name}.{attr}")

    @classmethod
    def clear_missing_variables(cls):
        cls._missing_variables.clear()

    @classmethod
    def raise_if_missing(cls):
        if cls._missing_variables:
            missing_list = "\n".join(f"- {v}" for v in sorted(cls._missing_variables))
            raise RuntimeError(f"❌ Missing template variables:\n{missing_list}")
