# create_db.py

import os
from flask import current_app
from app.app import create_app
from werkzeug.security import generate_password_hash

# # Configure logging
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

from app.utils.app_logging import get_logger

logger = get_logger()


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
            _create_or_update_sample_data(db)

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


def _create_or_update_sample_data(db):
    """Create or update sample data, avoiding duplicates."""
    logger.info("Creating or updating sample data...")

    # Create or update each type of sample data
    _create_sample_users(db)
    _create_sample_companies(db)
    _create_sample_contacts(db)
    _create_sample_opportunities(db)
    _create_sample_srs_items(db)


def _create_sample_users(db):
    from app.models.user import User

    logger.info("Processing sample users...")
    password = generate_password_hash("password123")
    sample_users = [
        {
            "username": "john",
            "name": "John Doe",
            "email": "john@example.com",
            "password_hash": password,
        },
        {
            "username": "jane",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "password_hash": password,
        },
    ]

    added = 0
    for user_data in sample_users:
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if not existing_user:
            db.session.add(User(**user_data))
            added += 1

    db.session.commit()
    logger.info(f"✅ Added {added} new sample users.")


def _create_sample_companies(db):
    from app.models.company import Company

    logger.info("Processing sample companies...")
    sample_companies = [
        {"name": "Acme Inc", "description": "Technology company"},
        {"name": "Beta Corp", "description": "Manufacturing company"},
    ]

    added = 0
    for company_data in sample_companies:
        existing_company = Company.query.filter_by(name=company_data["name"]).first()
        if not existing_company:
            db.session.add(Company(**company_data))
            added += 1

    db.session.commit()
    logger.info(f"✅ Added {added} new sample companies.")


def _create_sample_contacts(db):
    from app.models.contact import Contact

    logger.info("Processing sample contacts...")
    sample_contacts = [
        {"id": 1, "first_name": "Test", "last_name": "User"},
        {"id": 2, "first_name": "Test2", "last_name": "User2"},
    ]

    added = 0
    for contact_data in sample_contacts:
        existing_contact = Contact.query.filter_by(id=contact_data["id"]).first()
        if not existing_contact:
            db.session.add(Contact(**contact_data))
            added += 1

    db.session.commit()
    logger.info(f"✅ Added {added} new sample contacts.")


def _create_sample_opportunities(db):
    from app.models.opportunity import Opportunity

    logger.info("Processing sample opportunities...")
    sample_opportunities = [
        {
            "name": "New Website",
            "description": "Build a new website",
            "status": "New",
            "stage": "Prospecting",
            "value": 10000,
            "company_id": 1,
        },
        {
            "name": "Software Upgrade",
            "description": "Upgrade ERP system",
            "status": "In Progress",
            "stage": "Negotiation",
            "value": 25000,
            "company_id": 2,
        },
    ]

    added = 0
    for opp_data in sample_opportunities:
        existing_opp = Opportunity.query.filter_by(name=opp_data["name"], company_id=opp_data["company_id"]).first()
        if not existing_opp:
            db.session.add(Opportunity(**opp_data))
            added += 1

    db.session.commit()
    logger.info(f"✅ Added {added} new sample opportunities.")


def _create_sample_srs_items(db):
    from app.models.srs_item import SRSItem

    logger.info("Processing example SRS cards...")
    sample_cards = [
        # Contact cards
        {"notable_type": "Contact", "notable_id": 1, "question": "What is Test User's last name?", "answer": "User"},
        {"notable_type": "Contact", "notable_id": 2, "question": "What is Test2 User2's first name?", "answer": "Test2"},
        {"notable_type": "Contact", "notable_id": 1, "question": "Which contact has ID #1?", "answer": "Test User"},
        # Company cards
        {"notable_type": "Company", "notable_id": 1, "question": "What industry is Acme Inc in?", "answer": "Technology company"},
        {"notable_type": "Company", "notable_id": 2, "question": "What is Beta Corp's main business?", "answer": "Manufacturing company"},
        # Opportunity cards
        {
            "notable_type": "Opportunity",
            "notable_id": 1,
            "question": "What is the value of the New Website opportunity?",
            "answer": "$10,000",
        },
        {
            "notable_type": "Opportunity",
            "notable_id": 2,
            "question": "What stage is the Software Upgrade opportunity in?",
            "answer": "Negotiation",
        },
        {
            "notable_type": "Opportunity",
            "notable_id": 2,
            "question": "Which company is associated with the Software Upgrade opportunity?",
            "answer": "Beta Corp (ID: 2)",
        },
    ]

    added = 0
    for card_data in sample_cards:
        existing_card = SRSItem.query.filter_by(
            notable_type=card_data["notable_type"], notable_id=card_data["notable_id"], question=card_data["question"]
        ).first()
        if not existing_card:
            db.session.add(SRSItem(**card_data))
            added += 1

    db.session.commit()
    logger.info(f"✅ Added {added} new example SRS cards.")


if __name__ == "__main__":
    app = create_app()
    init_db(app)
