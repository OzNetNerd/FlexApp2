import pytest
import logging
from flask import Flask
from app.app import create_app


@pytest.fixture
def app() -> Flask:
    """
    Creates and configures a Flask application instance for testing.

    Returns:
        Flask: A Flask application configured for tests.
    """
    # Silence debug logs during testing
    logging.getLogger("app.app").setLevel(logging.WARNING)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    yield app


@pytest.fixture
def client(app: Flask):
    """
    Provides a Flask test client to simulate HTTP requests.

    Args:
        app (Flask): The test app fixture.

    Returns:
        FlaskClient: The test client for sending requests to the app.
    """
    return app.test_client()
