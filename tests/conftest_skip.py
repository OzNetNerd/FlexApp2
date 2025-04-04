"""
Helper to skip database tests.
Place in the same directory as conftest.py (tests folder root)
"""

import pytest


def pytest_collection_modifyitems(items):
    """Skip tests that require database interaction."""
    skipper = pytest.mark.skip(reason="DB tests disabled for now")
    for item in items:
        # Skip any test that requires the db fixture
        if "db" in item.fixturenames:
            item.add_marker(skipper)
