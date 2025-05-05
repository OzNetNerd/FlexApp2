"""
Domain exceptions for the company aggregate.

This module defines exception classes specific to the company domain.
"""


class DomainException(Exception):
    """Base exception for all domain exceptions."""

    pass


class CompanyNotFoundError(DomainException):
    """
    Exception raised when a company cannot be found.

    This exception is thrown when attempting to retrieve, update, or perform
    operations on a company that does not exist in the repository.
    """

    pass


class CompanyOperationError(DomainException):
    """
    Exception raised when a company operation fails.

    This exception is thrown when an operation on a company entity
    (create, update, delete) cannot be completed due to a technical issue.
    """

    pass


class DuplicateCompanyError(DomainException):
    """
    Exception raised when attempting to create a company with a duplicate name.

    This exception is thrown when a company with the same name already exists.
    """

    pass


class InvalidCompanyDataError(DomainException):
    """
    Exception raised when company data is invalid.

    This exception is thrown when attempting to create or update a company
    with invalid data that violates domain rules.
    """

    pass
