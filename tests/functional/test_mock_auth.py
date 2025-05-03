from unittest.mock import MagicMock, patch


def test_login_flow_without_db(app, monkeypatch):
    """Test login flow without needing the database.

    This test mocks the database interaction by replacing the actual query for a user with
    a mocked user object. It ensures that the login flow works even without a real database.
    The test verifies that the user can log in with a mock email and password.

    Args:
        app (Flask): The Flask application fixture for running the app.
        monkeypatch (MonkeyPatch): A pytest fixture used to mock methods and functions.

    Asserts:
        - The response status code is 200 (success).
    """
    # Create a mock user
    user_mock = MagicMock()
    user_mock.email = "test@example.com"
    user_mock.is_authenticated = True
    user_mock.get_id.return_value = "1"  # Ensure get_id() returns a JSON-serializable value

    # Mock User.query.filter_by().first() to return our mock user
    with patch("app.routes.web.auth.User.query") as user_query_mock:
        user_query_mock.filter_by.return_value.first.return_value = user_mock

        # Mock check_password_hash to return True
        with patch("app.routes.web.auth.check_password_hash", return_value=True):
            # Test client
            with app.test_client() as client:
                # Send POST request to login endpoint
                response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"})
                # Your endpoint returns 200 not 302
                assert response.status_code == 200