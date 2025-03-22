from flask import Flask, current_app
import json
import os
import logging

logger = logging.getLogger(__name__)


def init_db(app: Flask):
    """Initialize the database and create default data if needed."""
    # Import here to avoid circular imports
    from models.base import db

    db.init_app(app)

    with app.app_context():
        # Log the database URI for debugging
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI']
        logger.debug(f"Initializing database at: {db_path}")

        # Create database tables
        db.create_all()

        # Create default table configurations if they don't exist
        _create_default_table_configs(db)

        # Create some sample data for development
        if app.debug:
            logger.debug("Debug mode detected, creating sample data if needed...")
            _create_sample_data(db)

        # Verify database was created
        db_file = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_file):
            logger.info(f"Database file created successfully at: {db_file}")
        else:
            logger.warning(f"Database file not found at expected location: {db_file}")


def _create_default_table_configs(db):
    """Create default table configurations."""
    # Import here to avoid circular imports
    from models.table_config import TableConfig

    logger.debug("Creating default table configurations.")
    # Your table config code here (commented out in your original)
    # ...
    logger.info("Default table configurations function called.")


def _create_sample_data(db):
    """Create sample data for development environment."""
    # Import models here to avoid circular imports
    from models.user import User
    from models.company import Company
    from models.contact import Contact
    from models.opportunity import Opportunity

    logger.debug("Creating sample data for development environment.")
    if User.query.count() == 0:
        logger.debug("Creating sample users...")
        # Create sample users
        users = [
            User(username='john', name='John Doe', email='john@example.com'),
            User(username='jane', name='Jane Smith', email='jane@example.com')
        ]
        db.session.add_all(users)
        db.session.commit()

        logger.debug("Creating sample companies...")
        # Create sample companies
        companies = [
            Company(name='Acme Inc', description='Technology company'),
            Company(name='Beta Corp', description='Manufacturing company')
        ]
        db.session.add_all(companies)
        db.session.commit()

        logger.debug("Creating sample contacts...")
        # Create sample contacts
        contacts = [
            Contact(id=1, first_name='Test', last_name='User'),
            Contact(id=2, first_name='Test2', last_name='User2')
        ]

        db.session.add_all(contacts)
        db.session.commit()

        logger.debug("Creating sample opportunities...")
        # Create sample opportunities
        opportunities = [
            Opportunity(name='New Website', description='Build a new website', status='New',
                        stage='Prospecting', value=10000, company_id=1),
            Opportunity(name='Software Upgrade', description='Upgrade ERP system', status='In Progress',
                        stage='Negotiation', value=25000, company_id=2)
        ]
        db.session.add_all(opportunities)
        db.session.commit()

        logger.info("Sample data created successfully.")
    else:
        logger.info("Database already contains data. Skipping sample data creation.")