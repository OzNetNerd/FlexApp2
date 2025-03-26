from flask.testing import FlaskClient
from flask import Response


def test_home_redirects_to_login(client: FlaskClient):
    """
    Test that the home page redirects unauthenticated users to the login page.

    Args:
        client (FlaskClient): The test client.
    """
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [302, 308]

    location = response.headers.get("Location", "")
    assert "/auth/login" in location
    assert "next=/" in location  # ensures redirection remembers where user wanted to go


def test_protected_redirects_to_login(client: FlaskClient):
    """
    Ensure protected routes redirect unauthenticated users to the login page.

    Args:
        client (FlaskClient): The test client.
    """
    response: Response = client.get("/opportunities/", follow_redirects=False)
    assert response.status_code in [302, 308, 401]
    if response.status_code in [302, 308]:
        assert "login" in response.headers.get("Location", "")


def test_login_page_loads(client: FlaskClient):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"<form" in response.data  # more reliable than "Log In"
    assert b'action="/auth/login"' in response.data

