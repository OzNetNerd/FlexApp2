from flask.testing import FlaskClient


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
    assert "next=/" in location
