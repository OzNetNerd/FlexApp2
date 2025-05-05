"""
GraphQL module initialization.

This module provides the necessary setup for integrating GraphQL
with a Flask application, using Strawberry and the defined schema.
"""
from strawberry.flask.views import GraphQLView
from src.interfaces.graphql.schema import schema
from src.interfaces.graphql.context import get_graphql_context


def init_graphql(app):
    """
    Initialize GraphQL endpoints in a Flask application.

    This function registers the GraphQL endpoint with the Flask app,
    configuring it with our schema and context provider.

    Args:
        app: The Flask application instance to configure

    Returns:
        None
    """
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True,  # Enable GraphiQL interface for development
            context_getter=get_graphql_context
        )
    )