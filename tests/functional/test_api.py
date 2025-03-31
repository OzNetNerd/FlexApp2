"""Tests for the API endpoints.

This module tests the data API endpoints for the various entities in the application.
"""

import pytest
import json


class TestEntityAPI:
    """Tests for the entity data API endpoints."""

    @pytest.mark.parametrize("route,entity_name", [
        ("/companies/data", "Company"),
        ("/contacts/data", "Contact"),
        ("/opportunities/data", "Opportunity"),
        ("/users/data", "User"),
        ("/tasks/data", "Task")
    ])
    def test_data_api_returns_json(self, logged_in_client, route, entity_name):
        """Test that the data API endpoint returns valid JSON data."""
        response = logged_in_client.get(route)
        assert response.status_code == 200
        assert response.content_type == "application/json"

        # Verify the response is valid JSON
        data = json.loads(response.data)

        # Check for expected data structure (adjust based on your actual API response)
        assert "data" in data, f"Expected 'data' key in response for {entity_name}"

        # For this test, we just check if there's at least one record
        # More specific tests would depend on your exact data structure
        if entity_name == "Company":
            assert len(data["data"]) >= 1, "Expected at least one company record"
            # Verify the test company exists
            assert any(item["name"] == "Company 1" for item in data["data"]), "Test company not found"

        # Add similar checks for other entities based on your test data

    def test_data_api_authentication(self, client):
        """Test that unauthenticated users cannot access data API endpoints."""
        routes = [
            "/companies/data",
            "/contacts/data",
            "/opportunities/data",
            "/users/data",
            "/tasks/data"
        ]

        for route in routes:
            response = client.get(route, follow_redirects=False)
            # Should either redirect (302/303) or return unauthorized (401)
            assert response.status_code in [302, 303, 401], \
                f"Expected redirect or unauthorized for unauthenticated access to {route}, got {response.status_code}"


class TestSpecificEntityAPI:
    """Tests for specific entity API interactions."""

    def test_company_api(self, logged_in_client):
        """Test company-specific API functionality."""
        response = logged_in_client.get("/companies/data")
        assert response.status_code == 200

        data = json.loads(response.data)
        companies = data["data"]

        # Find the test company
        test_company = next((c for c in companies if c["name"] == "Company 1"), None)
        assert test_company is not None, "Test company not found in API response"

        # Verify the company details match what's in the test fixtures
        assert test_company["description"] == "Description of Company 1"

        # Keep the company_id for further tests
        company_id = test_company["id"]

        # Test retrieving the individual company
        response = logged_in_client.get(f"/companies/{company_id}")
        assert response.status_code == 200

    def test_contact_api(self, logged_in_client):
        """Test contact-specific API functionality."""
        response = logged_in_client.get("/contacts/data")
        assert response.status_code == 200

        data = json.loads(response.data)
        contacts = data["data"]

        # Verify the test contact exists
        test_contact = next((c for c in contacts if c["first_name"] == "John" and c["last_name"] == "Doe"), None)
        assert test_contact is not None, "Test contact not found in API response"
        assert test_contact["email"] == "johndoe@example.com", "Contact email doesn't match test data"

    def test_opportunity_api(self, logged_in_client):
        """Test opportunity-specific API functionality."""
        response = logged_in_client.get("/opportunities/data")
        assert response.status_code == 200

        data = json.loads(response.data)
        opportunities = data["data"]

        # Verify the test opportunity exists
        test_opportunity = next((o for o in opportunities if o["name"] == "Opportunity 1"), None)
        assert test_opportunity is not None, "Test opportunity not found in API response"
        assert test_opportunity["stage"] == "Prospecting", "Opportunity stage doesn't match test data"
        assert test_opportunity["value"] == 10000.0, "Opportunity value doesn't match test data"