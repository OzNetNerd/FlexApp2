"""Tests for page rendering functionality.

This module provides base test classes and fixtures for testing various page types
in the Flask application.
"""

import pytest
from flask import url_for
from bs4 import BeautifulSoup


class BasePageTest:
    """Base class for page testing with common assertions and utilities."""

    @staticmethod
    def get_soup(response):
        """Convert HTML response to BeautifulSoup object for easier testing."""
        return BeautifulSoup(response.data, 'html.parser')

    def assert_page_title(self, soup, expected_title):
        """Assert the page title is as expected."""
        title = soup.find('title')
        assert title is not None, "Page title element not found"
        assert title.text == expected_title, f"Expected title '{expected_title}', got '{title.text}'"

    def assert_navbar_active(self, soup, expected_active):
        """Assert the correct navbar item is active."""
        active_link = soup.select('.nav-link.active')
        assert len(active_link) == 1, f"Expected exactly one active nav link, found {len(active_link)}"
        assert expected_active in active_link[
            0].text.strip(), f"Expected '{expected_active}' to be active, got '{active_link[0].text.strip()}'"

    def assert_user_authenticated(self, soup, username):
        """Assert user info is displayed in the navbar."""
        user_name = soup.select('.user-name')
        assert len(user_name) > 0, "User name not found in navbar"
        assert username in user_name[
            0].text.strip(), f"Expected username '{username}', got '{user_name[0].text.strip()}'"

    def assert_add_button(self, soup, entity_name):
        """Assert the add button for the entity is present."""
        add_button = soup.find('a', class_='btn-primary')
        assert add_button is not None, "Add button not found"
        assert f"Add {entity_name}" in add_button.text.strip(), f"Expected 'Add {entity_name}' button, got '{add_button.text.strip()}'"

    def assert_table_present(self, soup):
        """Assert the data table is present."""
        table_container = soup.find(id='table-container')
        assert table_container is not None, "Table container not found"

    def assert_search_present(self, soup):
        """Assert the search input is present."""
        search_input = soup.find(id='globalSearch')
        assert search_input is not None, "Search input not found"


class ListPageTest(BasePageTest):
    """Test class for entity list pages."""

    def test_page_renders(self, logged_in_client, route, expected_title, entity_name, test_user):
        """Test that the entity list page renders correctly."""
        response = logged_in_client.get(route)
        assert response.status_code == 200

        soup = self.get_soup(response)
        self.assert_page_title(soup, expected_title)
        self.assert_navbar_active(soup, entity_name)
        self.assert_user_authenticated(soup, test_user.name)
        self.assert_add_button(soup, entity_name)
        self.assert_table_present(soup)
        self.assert_search_present(soup)

        # Check if heading and page title match
        heading = soup.find('h3', class_='text-primary')
        assert heading is not None, "Page heading not found"
        assert heading.text.strip() in [expected_title, f"{expected_title}s"], \
            f"Expected heading '{expected_title}', got '{heading.text.strip()}'"