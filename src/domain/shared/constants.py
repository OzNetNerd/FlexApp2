# src/domain/shared/constants.py

"""
Application-wide constants.

This module defines constants used throughout the application.
"""

# Navigation bar entries for the web interface
NAVBAR_ENTRIES = {
    "navbar_entries": [
        {"name": "Home", "url": "/", "icon": "home"},
        {"name": "Users", "url": "/users", "icon": "user"},
        {"name": "Companies", "url": "/companies", "icon": "building"},
        {"name": "Contacts", "url": "/contacts", "icon": "address-book"},
        {"name": "Opportunities", "url": "/opportunities", "icon": "bullseye"},
        {"name": "Tasks", "url": "/tasks", "icon": "check-square"},
        {"name": "Flash Cards", "url": "/srs", "icon": "book"},
    ]
}