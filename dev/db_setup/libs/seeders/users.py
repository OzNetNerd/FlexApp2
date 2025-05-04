# seeders/users.py - User seeder

import logging
from werkzeug.security import generate_password_hash

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models.pages.user import User

logger = logging.getLogger(__name__)

def seed_users():
    """Seed users into the database."""
    users = [
        ("morgan", "Morgan Chen", "morgan.chen@example.com", False),
        ("taylor", "Taylor Rodriguez", "taylor.rodriguez@example.com", False),
        ("jordan", "Jordan Patel", "jordan.patel@example.com", False),
        ("alex", "Alex Singh", "alex.singh@example.com", False),
        ("casey", "Casey Washington", "casey.washington@example.com", False),
        ("admin", "Admin User", "admin@example.com", True),
    ]

    for username, name, email, is_admin in users:
        create_or_update(
            User,
            {"username": username},
            {
                "name": name,
                "email": email,
                "password_hash": generate_password_hash("password"),
                "is_admin": is_admin,
            },
        )
    safe_commit()
    logger.info("✅ Users seeded.")