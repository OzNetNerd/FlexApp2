"""
Mock data for tests.

This file contains mock user data that is used for testing various parts of the application.
It provides test users with different attributes to simulate different user states (e.g., active, inactive).
"""

# Mock user data
TEST_USERS = [
    {"id": 1, "email": "test@example.com", "username": "test_user", "password": "password123", "name": "Test User"},
    {"id": 2, "email": "admin@example.com", "username": "admin_user", "password": "adminpass", "name": "Admin User"},
    {"id": 3, "email": "inactive@example.com", "username": "inactive_user", "password": "inactivepass", "name": "Inactive User"},
]
