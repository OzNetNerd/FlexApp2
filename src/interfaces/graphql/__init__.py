# src/interfaces/graphql/__init__.py

"""
GraphQL API initialization.

This module initializes the GraphQL API interface for the application.
"""

from flask import Flask


def init_graphql(app: Flask):
    """
    Initialize the GraphQL API for the Flask application.

    Args:
        app: Flask application instance.
    """
    # Import the schema module to register the schema
    from src.interfaces.graphql.schema import schema

    # Configure the GraphQL endpoint
    # This is a placeholder - you'll need to add actual implementation
    # based on your GraphQL library (e.g., Ariadne, Strawberry, etc.)
    pass