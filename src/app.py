# src/app.py

"""
Application entry point to initialize and run the Flask application.

This module serves as the main entry point to create and configure the
Flask application instance using a Domain-Driven Design architecture.
"""

from src.infrastructure.flask.app_factory import create_app
from config import Config

if __name__ == "__main__":
    app = create_app(Config)
    app.run(debug=True)