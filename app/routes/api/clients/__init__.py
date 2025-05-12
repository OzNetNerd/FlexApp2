# app/clients/__init__.py

import requests
from flask import current_app, url_for
from urllib.parse import urljoin


class ApiClient:
    """Base class for API clients."""

    def __init__(self, base_path):
        self.base_path = base_path

    def _get_base_url(self):
        """Get the base URL for API requests."""
        # In a production environment, this might be a configuration parameter
        server_name = current_app.config.get("SERVER_NAME", "localhost:5000")
        scheme = current_app.config.get("PREFERRED_URL_SCHEME", "http")
        return f"{scheme}://{server_name}"

    def _make_request(self, method, endpoint, params=None, data=None):
        """Make a request to the API.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            data (dict, optional): Request body for POST/PUT

        Returns:
            dict: JSON response from the API
        """
        url = urljoin(self._get_base_url(), endpoint)
        response = requests.request(method, url, params=params, json=data)
        response.raise_for_status()

        # Handle empty responses
        if not response.text:
            return {}

        # Try to parse as JSON, return empty dict if it fails
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {}

    def get(self, endpoint, params=None):
        """Make a GET request to the API."""
        return self._make_request('GET', endpoint, params=params)

    def post(self, endpoint, data):
        """Make a POST request to the API."""
        return self._make_request('POST', endpoint, data=data)

    def put(self, endpoint, data):
        """Make a PUT request to the API."""
        return self._make_request('PUT', endpoint, data=data)

    def delete(self, endpoint):
        """Make a DELETE request to the API."""
        return self._make_request('DELETE', endpoint)