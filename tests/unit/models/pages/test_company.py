"""
Unit tests for Company model.

These tests verify the existence and functionality of the Company model
in a DRY (Don't Repeat Yourself) manner.
"""

import os
import sys
import pytest
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import Company directly from the correct path
from app.models.pages.company import Company


@pytest.fixture
def company_instance():
    """Fixture that provides a Company instance for testing."""
    return Company(name="Test Company", description="Test Description")


@pytest.fixture
def clean_db(db):
    """Clean database tables before tests to avoid unique constraint violations."""
    # Clear relevant tables
    db.session.execute(text("DELETE FROM users"))
    db.session.execute(text("DELETE FROM companies"))
    db.session.commit()
    return db


def test_company_model_exists():
    """Verify that the Company model exists and can be imported."""
    assert Company is not None


@pytest.mark.parametrize("attribute", ["id", "name", "description"])
def test_company_attribute(company_instance, attribute):
    """Verify that the Company model has the expected attributes."""
    assert hasattr(company_instance, attribute)


@pytest.mark.parametrize("relationship", ["contacts", "opportunities", "notes", "company_capabilities"])
def test_company_relationship(company_instance, relationship):
    """Verify that the Company model has the expected relationships."""
    assert hasattr(company_instance, relationship)


def test_company_repr(company_instance):
    """Verify that the __repr__ method returns the expected string."""
    assert repr(company_instance) == "<Company 'Test Company'>"


@pytest.mark.db
class TestCompanyDatabase:
    """Database tests for the Company model."""

    def test_crud_operations(self, clean_db):
        """Test CRUD (Create, Read, Update, Delete) operations."""
        db = clean_db

        # Create
        company = Company(name="DB Test Company", description="DB Test Description")
        db.session.add(company)
        db.session.commit()

        company_id = company.id
        assert company_id is not None

        # Read
        retrieved = db.session.get(Company, company_id)
        assert retrieved.name == "DB Test Company"
        assert retrieved.description == "DB Test Description"

        # Update
        retrieved.name = "Updated Company"
        db.session.commit()
        updated = db.session.get(Company, company_id)
        assert updated.name == "Updated Company"

        # Delete
        db.session.delete(updated)
        db.session.commit()
        deleted = db.session.get(Company, company_id)
        assert deleted is None

    def test_nullable_constraints(self, clean_db):
        """Test NOT NULL constraints on required fields."""
        db = clean_db

        invalid_company = Company(description="No Name")
        db.session.add(invalid_company)

        with pytest.raises(Exception):
            db.session.commit()

        db.session.rollback()
