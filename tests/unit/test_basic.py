"""
A simple test to check if our basic test setup works.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_basic():
    """A simple test that always passes."""
    assert True