#!/usr/bin/env python3
import os
import logging
from flask import current_app
from app.app import create_app
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(app):
    """Initialize the database and create default data if needed."""
    from app.models.base import db

    with app.app_context():
        db_path = current_app.config["SQLALCHEMY_DATABASE_URI"]
        logger.info(f"Initializing database at: {db_path}")

        db.create_all()

        _create_default_table_configs(db)

        if app.debug:
            logger.info("Debug mode detected, creating sample data...")
            _create_sample_data(db)

        db_file = db_path.replace("sqlite:///", "")
        if os.path.exists(db_file):
            logger.info(f"✅ Database created at: {db_file}")
        else:
            logger.warning(f"⚠️ Expected database file not found at: {db_file}")


def _create_default_table_configs(db):
    from app.models.table_config import TableConfig

    logger.info("Creating default table configurations...")
    # Add any default table config creation logic here
    logger.info("✅ Default table configurations processed.")


def _create_sample_data(db):
    from app.models.user import User
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.opportunity import Opportunity

    if User.query.count() > 0:
        logger.info("Database already contains data. Skipping sample data creation.")
        return

    logger.info("Creating sample users...")
    password = generate_password_hash("password123")
    users = [
        User(
            username="john",
            name="John Doe",
            email="john@example.com",
            password_hash=password,
        ),
        User(
            username="jane",
            name="Jane Smith",
            email="jane@example.com",
            password_hash=password,
        ),
    ]
    db.session.add_all(users)
    db.session.commit()

    logger.info("Creating sample companies...")
    companies = [
        Company(name="Acme Inc", description="Technology company"),
        Company(name="Beta Corp", description="Manufacturing company"),
    ]
    db.session.add_all(companies)
    db.session.commit()

    logger.info("Creating sample contacts...")
    contacts = [
        Contact(id=1, first_name="Test", last_name="User"),
        Contact(id=2, first_name="Test2", last_name="User2"),
    ]
    db.session.add_all(contacts)
    db.session.commit()

    logger.info("Creating sample opportunities...")
    opportunities = [
        Opportunity(
            name="New Website",
            description="Build a new website",
            status="New",
            stage="Prospecting",
            value=10000,
            company_id=1,
        ),
        Opportunity(
            name="Software Upgrade",
            description="Upgrade ERP system",
            status="In Progress",
            stage="Negotiation",
            value=25000,
            company_id=2,
        ),
    ]
    db.session.add_all(opportunities)
    db.session.commit()

    logger.info("✅ Sample data created successfully.")


if __name__ == "__main__":
    app = create_app()
    init_db(app)
