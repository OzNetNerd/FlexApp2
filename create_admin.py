#!/usr/bin/env python3
from app.app import create_app
from app.models import User, db
from werkzeug.security import generate_password_hash


def create_admin_user():
    app = create_app()

    with app.app_context():
        # Admin user properties
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_data = {
            "username": admin_username,
            "name": "Administrator",
            "password_hash": generate_password_hash("password"),  # Change this!
            "is_admin": True,
        }

        # Check for existing admin by username OR email
        existing = User.query.filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()

        if existing:
            # Update existing admin user
            for key, value in admin_data.items():
                setattr(existing, key, value)
            existing.email = admin_email  # Ensure email is updated too
            db.session.commit()
            print("✅ Admin user updated.")
        else:
            # Create new admin user
            admin = User(email=admin_email, **admin_data)
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created.")


if __name__ == "__main__":
    create_admin_user()
