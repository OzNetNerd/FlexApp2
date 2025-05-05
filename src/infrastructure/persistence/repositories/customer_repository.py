"""Repository implementation for the company domain."""

from typing import List, Optional

from src.infrastructure.persistence.models.company import Company as CompanyModel
from domain.company.entities import Company
from domain.shared.interfaces.repository import Repository
from src.infrastructure.flask.extensions import db


class CompanyRepository(Repository):
    """
    Repository for company entities.

    Handles persistence operations for company domain entities.
    """

    def get_by_id(self, id: int) -> Optional[Company]:
        """
        Get a company by ID.

        Args:
            id: Company ID.

        Returns:
            Optional[Company]: The company entity or None if not found.
        """
        model = CompanyModel.query.get(id)
        if not model:
            return None
        return self._to_entity(model)

    def get_all(self) -> List[Company]:
        """
        Get all companies.

        Returns:
            List[Company]: List of all company entities.
        """
        models = CompanyModel.query.all()
        return [self._to_entity(model) for model in models]

    def get_by_name(self, name: str) -> Optional[Company]:
        """
        Get a company by name.

        Args:
            name: Company name.

        Returns:
            Optional[Company]: The company entity or None if not found.
        """
        model = CompanyModel.query.filter_by(name=name).first()
        if not model:
            return None
        return self._to_entity(model)

    def save(self, company: Company) -> Company:
        """
        Save a company entity.

        Args:
            company: Company entity to save.

        Returns:
            Company: The saved company entity.
        """
        if company.id:
            model = CompanyModel.query.get(company.id)
            if model:
                model.name = company.name
                model.description = company.description
            else:
                model = self._to_model(company)
                db.session.add(model)
        else:
            model = self._to_model(company)
            db.session.add(model)

        db.session.commit()
        company.id = model.id
        return company

    def delete(self, id: int) -> bool:
        """
        Delete a company by ID.

        Args:
            id: Company ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        model = CompanyModel.query.get(id)
        if not model:
            return False
        db.session.delete(model)
        db.session.commit()
        return True

    def _to_entity(self, model: CompanyModel) -> Company:
        """
        Convert ORM model to domain entity.

        Args:
            model: ORM model.

        Returns:
            Company: Domain entity.
        """
        return Company(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: Company) -> CompanyModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Domain entity.

        Returns:
            CompanyModel: ORM model.
        """
        return CompanyModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )