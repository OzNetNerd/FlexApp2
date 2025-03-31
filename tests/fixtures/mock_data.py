"""
Mock data for tests.
"""

from werkzeug.security import generate_password_hash

# Mock user data
TEST_USERS = [
    {
        'id': 1,
        'email': 'test@example.com',
        'password_hash': generate_password_hash('password123'),
        'name': 'Test User',
        'is_active': True
    },
    {
        'id': 2,
        'email': 'admin@example.com',
        'password_hash': generate_password_hash('adminpass'),
        'name': 'Admin User',
        'is_active': True
    },
    {
        'id': 3,
        'email': 'inactive@example.com',
        'password_hash': generate_password_hash('inactivepass'),
        'name': 'Inactive User',
        'is_active': False
    }
]