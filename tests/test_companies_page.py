"""Tests for the company view page functionality.

This module contains tests for verifying the correct rendering and
functionality of the company view page in the FlexApp application.
"""

import pytest
from flask_login import current_user
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_USER_NAME


@pytest.fixture
def response(logged_in_client):
    """
    Returns the HTTP response for the company view page after logging in.

    Args:
        logged_in_client: A logged-in Flask test client.

    Returns:
        The HTTP response from the company view page.
    """
    return logged_in_client.get('/companies/1', follow_redirects=True)


def test_status_code_ok(response) -> None:
    """Test that the company view page returns a 200 OK status code."""
    assert response.status_code == 200


def test_page_title_present(response) -> None:
    """Test that the page title is correct."""
    assert "<title>Viewing</title>" in response.data.decode()


def test_navbar_and_user_info_present(response) -> None:
    """Test that the navbar brand and user info are rendered correctly."""
    html = response.data.decode()
    assert "CRM Dashboard" in html
    assert TEST_USER_NAME in html
    assert TEST_USER_EMAIL in html


def test_tabs_exist(response) -> None:
    """Test that the About, Insights, and Metadata tabs exist."""
    html = response.data.decode()
    for tab_id in ['tab-about-tab', 'tab-insights-tab', 'tab-metadata-tab']:
        assert f'id="{tab_id}"' in html


def test_company_field_labels_present(response) -> None:
    """Test that all expected field labels are present on the page."""
    html = response.data.decode()
    for label in ["Name", "Description", "CRISP", "Created At", "Updated At"]:
        assert f'<span class="fw-bold">{label}</span>' in html


def test_company_field_values_present(response) -> None:
    """Test that company-specific field values are rendered correctly."""
    html = response.data.decode()
    assert "Company 1" in html
    assert "Description of Company 1" in html
    assert "No CRISP score available" in html
    assert "2025-03-30" in html  # Partial date match


def test_action_buttons_present(response) -> None:
    """Test that all action buttons (Add, Edit, Delete, Back) are present."""
    html = response.data.decode()
    for button in ['Add', 'Edit', 'Delete', 'Back']:
        assert button in html


def test_current_user_context(logged_in_client) -> None:
    """Test that current_user is authenticated and has the expected name."""
    with logged_in_client:
        response = logged_in_client.get("/companies/1")
        assert current_user.is_authenticated
        assert current_user.name == TEST_USER_NAME
