"""
Helper to skip database tests.

Place in the same directory as conftest.py (tests folder root) to temporarily
disable database-dependent tests. This allows faster test runs when only
testing non-database functionality.
"""

import pytest


def pytest_collection_modifyitems(items):
    """Skip tests that require database interaction."""
    skipper = pytest.mark.skip(reason="DB tests disabled for now")
    for item in items:
        # Skip any test that requires the db fixture or has the @pytest.mark.db marker
        if "db" in item.fixturenames or item.get_closest_marker("db"):
            item.add_marker(skipper)