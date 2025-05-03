"""
Unit tests for app.app_logging module.

Tests the logging utility functions and classes.
"""

import logging
import time
from io import StringIO

import pytest
from unittest.mock import patch, MagicMock


from app.utils.app_logging import (
    get_logger,
    log_instance_vars,
    log_message_and_variables,
    FunctionNameFilter,
    start_timer,
    log_elapsed,
    LoggingUndefined,
)


@pytest.fixture
def log_capture():
    """Fixture to capture log output"""
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))

    # Clear all handlers from the root logger
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    yield log_stream

    # Cleanup
    for h in root.handlers[:]:
        root.removeHandler(h)


@pytest.fixture(autouse=True)
def reset_logging_undefined():
    """Reset LoggingUndefined state before each test"""
    LoggingUndefined.clear_missing_variables()
    yield


def test_get_logger():
    """Test that get_logger returns a logger with the correct name"""
    logger = get_logger()
    # Check that logger name is the module name (test_app_logging)
    assert "test_app_logging" in logger.name


@patch("app.utils.app_logging.logger")
def test_log_instance_vars_no_exclusions(mock_logger):
    """Test log_instance_vars with no exclusions"""

    class TestClass:
        def __init__(self):
            self.attr1 = "value1"
            self.attr2 = "value2"
            self.private = "sensitive"

    instance = TestClass()

    log_instance_vars("TestClass instance", instance)

    mock_logger.info.assert_any_call("📋 Attributes for TestClass instance: ")
    mock_logger.info.assert_any_call("  📝 attr1: value1")
    mock_logger.info.assert_any_call("  📝 attr2: value2")
    mock_logger.info.assert_any_call("  📝 private: sensitive")
    mock_logger.info.assert_any_call("  ℹ️ (No exclusions)")


@patch("app.utils.app_logging.logger")
def test_log_instance_vars_with_exclusions(mock_logger):
    """Test log_instance_vars with exclusions"""

    class TestClass:
        def __init__(self):
            self.attr1 = "value1"
            self.attr2 = "value2"
            self.private = "sensitive"

    instance = TestClass()

    log_instance_vars("TestClass instance", instance, exclude=["private"])

    mock_logger.info.assert_any_call("📋 Attributes for TestClass instance: ")
    mock_logger.info.assert_any_call("  📝 attr1: value1")
    mock_logger.info.assert_any_call("  📝 attr2: value2")
    mock_logger.info.assert_any_call("  ℹ️ (Excluded: private)")


@patch("app.utils.app_logging.logger")
def test_log_message_and_variables(mock_logger):
    """Test logging message with variables"""
    variables = {"var1": "value1", "var2": 42, "var3": [1, 2, 3]}

    log_message_and_variables("Test message", variables)

    mock_logger.info.assert_any_call("Test message")
    mock_logger.info.assert_any_call("  📝 var1: value1")
    mock_logger.info.assert_any_call("  📝 var2: 42")
    mock_logger.info.assert_any_call("  📝 var3: [1, 2, 3]")


def test_function_name_filter():
    """Test FunctionNameFilter modifies function name in log records"""
    test_logger = logging.getLogger("test_filter")
    test_logger.setLevel(logging.INFO)

    # Clear handlers and add our own
    for handler in test_logger.handlers[:]:
        test_logger.removeHandler(handler)

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(funcName)s: %(message)s"))
    test_logger.addHandler(handler)

    # Add filter to change function name
    name_filter = FunctionNameFilter("custom_function")
    test_logger.addFilter(name_filter)

    # Log a message
    test_logger.info("Test message")

    # Check output
    assert stream.getvalue().strip() == "custom_function: Test message"

@patch("app.utils.app_logging.logger")
def test_start_timer_and_log_elapsed(mock_logger):
    """Test timer and elapsed time logging"""
    with patch("time.time") as mock_time:
        # First call to time.time() in start_timer
        mock_time.return_value = 1000.0
        timer = start_timer()
        assert timer == 1000.0

        # Second call to time.time() in log_elapsed
        mock_time.return_value = 1002.5

        with patch("app.utils.app_logging.logger") as mock_logger:
            log_elapsed(timer, "Operation completed")
            mock_logger.debug.assert_called_once_with('⏱️ Operation completed:  2.5000 seconds')


def test_logging_undefined_str():
    """Test LoggingUndefined string conversion"""
    undef = LoggingUndefined(name="missing_var")

    with patch("app.utils.app_logging.logger") as mock_logger:
        str_val = str(undef)

    assert str_val == "<<undefined: missing_var>>"
    mock_logger.warning.assert_called_with("⚠️  Undefined variable rendered as string: 'missing_var'")
    assert "missing_var" in LoggingUndefined._missing_variables


def test_logging_undefined_getitem():
    """Test LoggingUndefined item access"""
    undef = LoggingUndefined(name="missing_dict")

    with patch("app.utils.app_logging.logger") as mock_logger:
        item = undef["key"]

    assert isinstance(item, LoggingUndefined)
    mock_logger.warning.assert_called_with("⚠️  Attempted to access key 'key' on undefined variable: 'missing_dict'")
    assert "missing_dict" in LoggingUndefined._missing_variables


def test_logging_undefined_getattr():
    """Test LoggingUndefined attribute access"""
    undef = LoggingUndefined(name="missing_obj")

    with patch("app.utils.app_logging.logger") as mock_logger:
        attr = undef.attribute

    assert isinstance(attr, LoggingUndefined)
    mock_logger.warning.assert_called_with("⚠️  Attempted to access attribute 'attribute' on undefined variable: 'missing_obj'")
    assert "missing_obj" in LoggingUndefined._missing_variables


def test_logging_undefined_clear():
    """Test clearing missing variables"""
    undef1 = LoggingUndefined(hint=None, obj=None, name="var1")
    undef2 = LoggingUndefined(hint=None, obj=None, name="var2")
    str(undef1)  # This calls __str__ which calls _log
    str(undef2)  # This adds the variable to _missing_variables

    assert len(LoggingUndefined._missing_variables) >= 2
    LoggingUndefined.clear_missing_variables()
    assert len(LoggingUndefined._missing_variables) == 0


def test_logging_undefined_raise():
    """Test raising exception for missing variables"""
    undef3 = LoggingUndefined(hint=None, obj=None, name="var3")
    undef4 = LoggingUndefined(hint=None, obj=None, name="var4")

    # Trigger logging by converting to string
    str(undef3)
    str(undef4)

    with pytest.raises(RuntimeError) as excinfo:
        LoggingUndefined.raise_if_missing()

    error_msg = str(excinfo.value)
    assert "❌ Missing template variables:" in error_msg
    assert "- var3" in error_msg
    assert "- var4" in error_msg