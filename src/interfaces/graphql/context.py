"""
GraphQL context provider module.

This module provides the context creation function for GraphQL requests,
which includes essential components like UnitOfWork and DataLoaders.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from flask import request, g

from infrastructure.persistence.unit_of_work import UnitOfWork
from infrastructure.auth.services import get_current_user
from src.interfaces.graphql.dataloaders import create_dataloaders
from src.interfaces.graphql.dataloaders.base import DataLoaderContext


@dataclass
class GraphQLContext:
    """
    GraphQL request context container.

    This class holds all context objects needed during GraphQL
    query resolution, like user information, unit of work, and dataloaders.
    """
    request: Any
    unit_of_work: UnitOfWork
    loaders: DataLoaderContext
    user: Optional[Any] = None


def get_graphql_context(request_context=None) -> GraphQLContext:
    """
    Create the GraphQL context for the current request.

    This function creates a GraphQL context with all necessary components,
    including authentication state, unit of work, and dataloaders.

    Args:
        request_context: Optional Flask request context (used for testing)

    Returns:
        GraphQLContext: The constructed GraphQL context
    """
    # Use the provided request context or the current Flask request
    req = request_context or request

    # Create a new unit of work for this request
    unit_of_work = UnitOfWork()

    # Create dataloaders with the unit of work
    loaders = create_dataloaders(unit_of_work)

    # Get the current user if authenticated
    user = get_current_user(req)

    # Return the constructed context
    return GraphQLContext(
        request=req,
        unit_of_work=unit_of_work,
        loaders=DataLoaderContext(**loaders),
        user=user
    )