try:
    from config import Config
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from config import Config

from app.app import create_app
from app.models import User, db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_email = "admin@example.com"
    existing = User.query.filter_by(email=admin_email).first()

    if not existing:
        admin = User(
            username="admin",
            name="Administrator",
            email=admin_email,
            password_hash=generate_password_hash("password"),  # Change this!
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created.")
    else:
        print("⚠️ Admin user already exists.")
