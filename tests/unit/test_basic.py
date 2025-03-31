"""
A simple test to check if our basic test setup works.

This test verifies that the testing setup is working correctly by running a basic assertion
that always passes. It is used to confirm that the test environment is properly configured.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_basic():
    """A simple test that always passes.

    This test ensures that the test environment is set up correctly and that basic assertions
    are working. It is a placeholder test to confirm that tests can be executed successfully.

    Asserts:
        - True (this is a trivial test that always passes).
    """
    assert True
