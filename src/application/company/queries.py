"""
Company query objects for the application layer.

This module contains query objects that retrieve company data according to
Domain-Driven Design principles, separating query concerns from command concerns.
"""
from dataclasses import dataclass
from typing import List, Optional, Any

from src.application.company.dto import CompanyDTO, CompanyDetailsDTO
from src.domain.company.repositories import CompanyRepository


@dataclass
class GetCompanyQuery:
    """
    Query to retrieve a single company by ID.

    Attributes:
        company_id: The ID of the company to retrieve
    """
    company_id: int

    async def execute(self, repository: CompanyRepository) -> Optional[CompanyDTO]:
        """
        Execute the query using the provided repository.

        Args:
            repository: The repository to use for data retrieval

        Returns:
            Optional[CompanyDTO]: The company data transfer object if found, None otherwise
        """
        company = await repository.get_by_id(self.company_id)
        if not company:
            return None

        return CompanyDTO.from_entity(company)


@dataclass
class ListCompaniesQuery:
    """
    Query to retrieve a paginated list of companies.

    Attributes:
        limit: Maximum number of companies to return
        offset: Number of companies to skip
        filters: Optional dictionary of filters to apply
    """
    limit: int = 20
    offset: int = 0
    filters: Optional[dict] = None

    async def execute(self, repository: CompanyRepository) -> List[CompanyDTO]:
        """
        Execute the query using the provided repository.

        Args:
            repository: The repository to use for data retrieval

        Returns:
            List[CompanyDTO]: List of company data transfer objects
        """
        companies = await repository.get_paginated(self.limit, self.offset, self.filters)
        return [CompanyDTO.from_entity(company) for company in companies]


@dataclass
class GetCompanyDetailsQuery:
    """
    Query to retrieve detailed information about a company.

    Attributes:
        company_id: The ID of the company to retrieve details for
    """
    company_id: int

    async def execute(self, repository: CompanyRepository) -> Optional[CompanyDetailsDTO]:
        """
        Execute the query using the provided repository.

        Args:
            repository: The repository to use for data retrieval

        Returns:
            Optional[CompanyDetailsDTO]: Detailed company information if found, None otherwise
        """
        company = await repository.get_by_id_with_details(self.company_id)
        if not company:
            return None

        return CompanyDetailsDTO.from_entity(company)


# For convenience, add a function that resolves the appropriate repository
async def execute_company_query(query: Any, unit_of_work: Any) -> Any:
    """
    Helper function to execute a company query with the appropriate repository.

    Args:
        query: The query object to execute
        unit_of_work: The unit of work containing repositories

    Returns:
        The result of executing the query
    """
    with unit_of_work:
        repository = unit_of_work.company_repository
        return await query.execute(repository)