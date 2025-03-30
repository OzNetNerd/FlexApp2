"""Tests for the company view page functionality.

This module contains tests for verifying the correct rendering and
functionality of the company view page in the FlexApp application.
"""

import pytest
from flask_login import current_user

# Suppress SADeprecationWarning without trying to patch internals
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application.

    Args:
        app: The Flask application fixture.

    Returns:
        A Flask test client.
    """
    return app.test_client()


@pytest.fixture
def response(client):
    """Create an authenticated session and return the company view page response.

    Args:
        client: The Flask test client.

    Returns:
        The HTTP response from the company view page.
    """
    with client:
        client.post(
            "/auth/login",
            data={"email": "newadmin@example.com", "password": "password"},
            follow_redirects=True
        )
        return client.get('/companies/1', follow_redirects=True)


def test_status_code_ok(response) -> None:
    """Test that the company view page returns a 200 OK status code.

    Args:
        response: The HTTP response fixture.
    """
    assert response.status_code == 200


def test_title_present(response) -> None:
    """Test that the page title is correct.

    Args:
        response: The HTTP response fixture.
    """
    assert "<title>Viewing</title>" in response.data.decode()


def test_navbar_brand(response) -> None:
    """Test that the navbar brand text is present.

    Args:
        response: The HTTP response fixture.
    """
    assert "CRM Dashboard" in response.data.decode()


def test_tabs_exist(response) -> None:
    """Test that the about and insights tabs exist on the page.

    Args:
        response: The HTTP response fixture.
    """
    html = response.data.decode()
    assert 'id="tab-about-tab"' in html
    assert 'id="tab-insights-tab"' in html


def test_company_details_section_present(response) -> None:
    """Test that the company details section is present.

    Args:
        response: The HTTP response fixture.
    """
    assert "Company Details" in response.data.decode()


def test_crisp_score_section_present(response) -> None:
    """Test that the CRISP score section is present.

    Args:
        response: The HTTP response fixture.
    """
    assert "CRISP Score" in response.data.decode()


def test_buttons_present(response) -> None:
    """Test that all required action buttons are present.

    Args:
        response: The HTTP response fixture.
    """
    html = response.data.decode()
    for button in ['Add', 'Edit', 'Delete', 'Back']:
        assert button in html


def test_user_avatar_present(client) -> None:
    """Test that the authenticated user's avatar and details are present.

    Args:
        client: The Flask test client.
    """
    with client:
        client.post(
            "/auth/login",
            data={"email": "newadmin@example.com", "password": "password"},
            follow_redirects=True
        )
        client.get("/companies/1")
        assert current_user.is_authenticated
        assert current_user.name == "Test Admin"


def test_field_name_label_present(response) -> None:
    """Test that the Name field label is present.

    Args:
        response: The HTTP response fixture.
    """
    assert '<span class="fw-bold">Name</span>' in response.data.decode()


def test_field_description_label_present(response) -> None:
    """Test that the Description field label is present.

    Args:
        response: The HTTP response fixture.
    """
    assert '<span class="fw-bold">Description</span>' in response.data.decode()


def test_field_crisp_label_present(response) -> None:
    """Test that the CRISP field label is present.

    Args:
        response: The HTTP response fixture.
    """
    assert '<span class="fw-bold">CRISP</span>' in response.data.decode()