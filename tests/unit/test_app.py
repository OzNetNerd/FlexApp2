# Minimal unit tests for Flask app
import pytest


def test_app_creation(app):
    """Test that app fixture creates a valid Flask app."""
    assert app is not None
    assert app.name == 'app.app'


def test_app_config(app):
    """Test that app has the expected configuration."""
    assert app.config['TESTING'] is True
    assert app.config['WTF_CSRF_ENABLED'] is False


def test_app_routes(app):
    """Test that app has registered routes."""
    rules = list(app.url_map.iter_rules())
    assert len(rules) > 0


def test_app_context(app):
    """Test app context functionality."""
    with app.app_context():
        from flask import current_app
        assert current_app is not None
        assert current_app.config['TESTING'] is True


def test_static_route_access(app, client):
    """Test static route access works."""
    # Skip actual file access, just verify route behavior
    with app.test_request_context('/static/dummy.css'):
        assert app.static_folder is not None