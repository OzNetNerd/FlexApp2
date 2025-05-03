"""
Mock data for tests.

This file contains mock user data that is used for testing various parts of the application.
It provides test users with different attributes to simulate different user states.
"""

import hashlib


# Generate a simple hash for testing purposes (not for production use)
def generate_test_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


# Mock user data with password_hash field
TEST_USERS = [
    {
        "id": 1,
        "email": "test@example.com",
        "username": "test_user",
        "password": "password123",  # Plain password for login tests
        "password_hash": generate_test_hash("password123"),  # Hashed password for model tests
        "name": "Test User",
    },
    {
        "id": 2,
        "email": "admin@example.com",
        "username": "admin_user",
        "password": "adminpass",
        "password_hash": generate_test_hash("adminpass"),
        "name": "Admin User",
    },
    {
        "id": 3,
        "email": "inactive@example.com",
        "username": "inactive_user",
        "password": "inactivepass",
        "password_hash": generate_test_hash("inactivepass"),
        "name": "Inactive User",
    },
]
