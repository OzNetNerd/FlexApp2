"""
DataLoader initialization module.

This module provides factory functions to create all necessary
data loaders for the GraphQL context.
"""
from src.interfaces.graphql.dataloaders.company import CompanyLoader
from src.interfaces.graphql.dataloaders.customer import CustomerLoader
from src.interfaces.graphql.dataloaders.opportunity import OpportunityLoader


def create_dataloaders(unit_of_work):
    """
    Create and initialize all DataLoaders with the provided unit of work.

    Args:
        unit_of_work: The UnitOfWork instance for database operations

    Returns:
        dict: A dictionary containing all initialized DataLoaders
    """
    return {
        "company": CompanyLoader(unit_of_work),
        "customer": CustomerLoader(unit_of_work),
        "opportunity": OpportunityLoader(unit_of_work)
    }