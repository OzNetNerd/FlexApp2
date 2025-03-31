"""Tests for entity pages.

This module contains tests for the various entity pages in the application,
utilizing the base test classes and fixtures from the base module.
"""

import pytest
from tests.functional.test_base_page import ListPageTest


@pytest.fixture
def entity_test_params():
    """Fixture that returns parameters for testing different entity pages."""
    return [
        {
            "route": "/companies/",
            "expected_title": "Companys",
            "entity_name": "Company",
            "endpoint": "companies.index"
        },
        {
            "route": "/contacts/",
            "expected_title": "Contacts",
            "entity_name": "Contact",
            "endpoint": "contacts.index"
        },
        {
            "route": "/opportunities/",
            "expected_title": "Opportunitys",
            "entity_name": "Opportunity",
            "endpoint": "opportunities.index"
        },
        {
            "route": "/users/",
            "expected_title": "Users",
            "entity_name": "User",
            "endpoint": "users.index"
        },
        {
            "route": "/tasks/",
            "expected_title": "Tasks",
            "entity_name": "Task",
            "endpoint": "tasks.index"
        }
    ]


class TestEntities(ListPageTest):
    """Tests for entity list pages."""

    # Define test parameters directly to avoid fixture_func error
    entity_params = [
        {
            "route": "/companies/",
            "expected_title": "Companys",
            "entity_name": "Company",
            "endpoint": "companies.index"
        },
        {
            "route": "/contacts/",
            "expected_title": "Contacts",
            "entity_name": "Contact",
            "endpoint": "contacts.index"
        },
        {
            "route": "/opportunities/",
            "expected_title": "Opportunitys",
            "entity_name": "Opportunity",
            "endpoint": "opportunities.index"
        },
        {
            "route": "/users/",
            "expected_title": "Users",
            "entity_name": "User",
            "endpoint": "users.index"
        },
        {
            "route": "/tasks/",
            "expected_title": "Tasks",
            "entity_name": "Task",
            "endpoint": "tasks.index"
        }
    ]

    @pytest.mark.parametrize("params", entity_params, ids=lambda p: p["entity_name"])
    def test_entity_list_page(self, logged_in_client, test_user, params):
        """Test that entity list pages render correctly.

        This test will run for each entity type defined in the entity_params list.
        """
        self.test_page_renders(
            logged_in_client=logged_in_client,
            route=params["route"],
            expected_title=params["expected_title"],
            entity_name=params["entity_name"],
            test_user=test_user
        )

    def test_unauthorized_access(self, client, entity_test_params):
        """Test that unauthenticated users are redirected to login."""
        for params in entity_test_params:
            response = client.get(params["route"], follow_redirects=True)
            assert response.status_code == 200

            # Check for login form elements using string checks
            response_text = response.data.decode('utf-8')
            assert 'name="email"' in response_text, f"Login email input not found for {params['route']}"
            assert 'name="password"' in response_text, f"Login password input not found for {params['route']}"


class TestCreateEntityPages(ListPageTest):
    """Tests for create entity pages."""

    @pytest.mark.parametrize("params", TestEntities.entity_params, ids=lambda p: p["entity_name"])
    def test_create_entity_page(self, logged_in_client, test_user, params):
        """Test that entity creation pages render correctly."""
        create_route = f"{params['route']}create"
        response = logged_in_client.get(create_route)
        assert response.status_code == 200

        # Verify user is authenticated
        self.assert_user_authenticated(response, test_user.name)

        # Check for form elements
        response_text = response.data.decode('utf-8')
        assert '<form' in response_text, f"Form not found on {create_route}"

        # Look for headings that might contain the entity name or "Create"
        heading_found = False
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            pattern = f'<{tag}[^>]*>([^<]*{params["entity_name"]}|[^<]*Create[^<]*)</{tag}>'
            if re.search(pattern, response_text, re.IGNORECASE):
                heading_found = True
                break

        assert heading_found, f"No appropriate heading found on {create_route}"