# src/infrastructure/flask/extensions.py

"""
Flask extensions configuration.

This module initializes the Flask extensions used throughout the application.
"""

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
