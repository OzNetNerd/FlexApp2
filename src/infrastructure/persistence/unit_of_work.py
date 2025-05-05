"""
Unit of Work implementation.

This module provides the UnitOfWork class that orchestrates
repository access and transaction management for the application.
"""
from typing import Any, Optional, Type, TypeVar, Generic

from src.domain.company.repositories import CompanyRepository
from src.infrastructure.persistence.repositories.company_repository import SQLCompanyRepository

# Generic type for commands and queries
T = TypeVar('T')
R = TypeVar('R')


class UnitOfWork:
    """
    Unit of Work implementation for coordinating repository access and transactions.

    The Unit of Work pattern maintains a list of objects affected by a business
    transaction and coordinates the writing out of changes.
    """

    def __init__(self, session_factory=None):
        """
        Initialize a new Unit of Work.

        Args:
            session_factory: Optional session factory for database access
        """
        self.session_factory = session_factory
        self.session = None
        self._company_repository = None

    def __enter__(self):
        """
        Enter the context manager, starting a new database session.

        Returns:
            UnitOfWork: This unit of work instance
        """
        self.session = self.session_factory() if self.session_factory else None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, committing or rolling back the session as needed.

        Args:
            exc_type: Exception type, if raised
            exc_val: Exception value, if raised
            exc_tb: Exception traceback, if raised
        """
        if self.session is None:
            return

        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

        self.session.close()
        self.session = None

    def commit(self):
        """Commit the current transaction."""
        if self.session:
            self.session.commit()

    def rollback(self):
        """Roll back the current transaction."""
        if self.session:
            self.session.rollback()

    @property
    def company_repository(self) -> CompanyRepository:
        """
        Get the company repository instance.

        Returns:
            CompanyRepository: The repository instance
        """
        if self._company_repository is None:
            self._company_repository = SQLCompanyRepository(self.session)
        return self._company_repository

    async def execute_query(self, query: Any) -> Any:
        """
        Execute a query and return its result.

        This method determines the appropriate repository based on
        the query type and executes it within the current transaction.

        Args:
            query: The query object to execute

        Returns:
            Any: The result of executing the query
        """
        # Determine the domain area from the query's module
        module_name = query.__class__.__module__

        if 'company' in module_name:
            return await query.execute(self.company_repository)
        elif 'customer' in module_name:
            return await query.execute(self.customer_repository)
        elif 'opportunity' in module_name:
            return await query.execute(self.opportunity_repository)
        else:
            raise ValueError(f"Unknown query type: {query.__class__.__name__}")

    async def execute_command(self, command: Any) -> Any:
        """
        Execute a command and return its result.

        This method determines the appropriate service based on
        the command type, executes it, and commits the transaction.

        Args:
            command: The command object to execute

        Returns:
            Any: The result of executing the command
        """
        # Determine the domain area from the command's module
        module_name = command.__class__.__module__

        if 'company' in module_name:
            result = await command.execute(self.company_repository)
        elif 'customer' in module_name:
            result = await command.execute(self.customer_repository)
        elif 'opportunity' in module_name:
            result = await command.execute(self.opportunity_repository)
        else:
            raise ValueError(f"Unknown command type: {command.__class__.__name__}")

        # Commit the transaction after successful command execution
        self.commit()
        return result