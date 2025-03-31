"""Tests for form submission functionality.

This module tests the form submission and validation for the various entities.
"""

import pytest
from tests.functional.test_base_page import BasePageTest


class FormTestBase(BasePageTest):
    """Base class for form testing."""

    def assert_form_submission_success(self, client, url, form_data, success_url):
        """Assert that form submission succeeds and redirects correctly."""
        response = client.post(url, data=form_data, follow_redirects=True)
        assert response.status_code == 200

        # Check if we're on the expected success page
        current_url = response.request.path
        assert current_url == success_url, f"Expected redirect to {success_url}, got {current_url}"

    def assert_form_validation_error(self, client, url, form_data, field_name):
        """Assert that a form validation error occurs for the specified field."""
        response = client.post(url, data=form_data, follow_redirects=True)
        assert response.status_code == 200

        soup = self.get_soup(response)

        # Check for validation error messages
        error_fields = soup.select(f".invalid-feedback") or soup.select(f".text-danger")
        assert len(error_fields) > 0, "No validation errors found when errors were expected"

        # If field_name is specified, check for specific field error
        if field_name:
            field = soup.find("input", {"name": field_name}) or soup.find("select", {"name": field_name})
            assert field is not None, f"Field {field_name} not found in form"
            assert "is-invalid" in field.get("class", []), f"Field {field_name} is not marked as invalid"


class TestCompanyForms(FormTestBase):
    """Tests for company form submission."""

    def test_company_create_form(self, logged_in_client):
        """Test company creation form."""
        # Test successful submission
        form_data = {
            "name": "Test New Company",
            "description": "This is a test company created by automated tests",
            # Add other required fields based on your form
        }

        self.assert_form_submission_success(
            logged_in_client,
            "/companies/create",
            form_data,
            "/companies/"  # Expected redirect URL after success
        )

        # Test validation (missing required name)
        invalid_form_data = {
            "name": "",
            "description": "This is an invalid company"
        }

        self.assert_form_validation_error(
            logged_in_client,
            "/companies/create",
            invalid_form_data,
            "name"
        )


class TestContactForms(FormTestBase):
    """Tests for contact form submission."""

    def test_contact_create_form(self, logged_in_client):
        """Test contact creation form."""
        # Get company for association
        response = logged_in_client.get("/companies/data")
        import json
        data = json.loads(response.data)
        company_id = data["data"][0]["id"]

        # Test successful submission
        form_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "janesmith@example.com",
            "phone": "555-5678",
            "company_id": company_id,
            # Add other required fields based on your form
        }

        self.assert_form_submission_success(
            logged_in_client,
            "/contacts/create",
            form_data,
            "/contacts/"  # Expected redirect URL after success
        )

        # Test validation (missing required email)
        invalid_form_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "",  # Empty email should trigger validation
            "phone": "555-5678",
            "company_id": company_id,
        }

        self.assert_form_validation_error(
            logged_in_client,
            "/contacts/create",
            invalid_form_data,
            "email"
        )


class TestOpportunityForms(FormTestBase):
    """Tests for opportunity form submission."""

    def test_opportunity_create_form(self, logged_in_client):
        """Test opportunity creation form."""
        # Get company for association
        response = logged_in_client.get("/companies/data")
        import json
        data = json.loads(response.data)
        company_id = data["data"][0]["id"]

        # Test successful submission
        form_data = {
            "name": "New Business Opportunity",
            "description": "This is a test opportunity created by automated tests",
            "status": "New",
            "stage": "Prospecting",
            "value": "15000.00",
            "company_id": company_id,
            # Add other required fields based on your form
        }

        self.assert_form_submission_success(
            logged_in_client,
            "/opportunities/create",
            form_data,
            "/opportunities/"  # Expected redirect URL after success
        )

        # Test validation (invalid value format)
        invalid_form_data = {
            "name": "Bad Opportunity",
            "description": "This has invalid value",
            "status": "New",
            "stage": "Prospecting",
            "value": "not-a-number",  # Invalid number format
            "company_id": company_id,
        }

        self.assert_form_validation_error(
            logged_in_client,
            "/opportunities/create",
            invalid_form_data,
            "value"
        )


class TestTaskForms(FormTestBase):
    """Tests for task form submission."""

    def test_task_create_form(self, logged_in_client):
        """Test task creation form."""
        # Get company for association
        response = logged_in_client.get("/companies/data")
        import json
        data = json.loads(response.data)
        company_id = data["data"][0]["id"]

        # Test successful submission
        form_data = {
            "title": "Follow up call",
            "description": "Follow up with client about contract renewal",
            "status": "Pending",
            "priority": "High",
            "notable_type": "Company",
            "notable_id": company_id,
            # Add other required fields based on your form
        }

        self.assert_form_submission_success(
            logged_in_client,
            "/tasks/create",
            form_data,
            "/tasks/"  # Expected redirect URL after success
        )

        # Test validation (missing required title)
        invalid_form_data = {
            "title": "",  # Empty title should trigger validation
            "description": "Description without title",
            "status": "Pending",
            "priority": "High",
            "notable_type": "Company",
            "notable_id": company_id,
        }

        self.assert_form_validation_error(
            logged_in_client,
            "/tasks/create",
            invalid_form_data,
            "title"
        )