# seeders/relationships.py - Relationships seeder

import logging

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models import User, Contact, Company
from app.models.relationship import Relationship

logger = logging.getLogger(__name__)


def seed_relationships():
    """Seed relationships between entities in the database."""
    users = User.query.all()
    contacts = Contact.query.all()
    companies = Company.query.all()

    # Define relationship types relevant to cloud security sales
    relationship_types = [
        "Account Executive",
        "Solution Architect",
        "Technical Champion",
        "Economic Buyer",
        "Decision Maker",
        "Influencer",
        "Partner",
        "Channel Manager",
    ]

    # Create user-to-user relationships (internal team structure)
    create_or_update(
        Relationship,
        {
            "entity1_type": "user",
            "entity1_id": User.query.filter_by(username="morgan").first().id,
            "entity2_type": "user",
            "entity2_id": User.query.filter_by(username="taylor").first().id,
        },
        {"relationship_type": "Account Manager"},
    )

    create_or_update(
        Relationship,
        {
            "entity1_type": "user",
            "entity1_id": User.query.filter_by(username="taylor").first().id,
            "entity2_type": "user",
            "entity2_id": User.query.filter_by(username="jordan").first().id,
        },
        {"relationship_type": "Solution Architect"},
    )

    create_or_update(
        Relationship,
        {
            "entity1_type": "user",
            "entity1_id": User.query.filter_by(username="jordan").first().id,
            "entity2_type": "user",
            "entity2_id": User.query.filter_by(username="alex").first().id,
        },
        {"relationship_type": "Sales Engineer"},
    )

    create_or_update(
        Relationship,
        {
            "entity1_type": "user",
            "entity1_id": User.query.filter_by(username="casey").first().id,
            "entity2_type": "user",
            "entity2_id": User.query.filter_by(username="admin").first().id,
        },
        {"relationship_type": "Reports To"},
    )

    # Create realistic user-to-contact relationships
    relationships = [
        ("morgan", "James Wilson", "Account Executive"),
        ("taylor", "Sarah Martinez", "Solution Architect"),
        ("jordan", "Michael Thompson", "Technical Advisor"),
        ("alex", "Emily Johnson", "Sales Engineer"),
        ("casey", "David Patel", "Account Manager"),
        ("morgan", "Jennifer Garcia", "Executive Sponsor"),
        ("taylor", "Robert Kim", "Technical Champion"),
    ]

    for username, contact_name, rel_type in relationships:
        user = User.query.filter_by(username=username).first()
        first_name, last_name = contact_name.split(" ", 1)
        contact = Contact.query.filter_by(first_name=first_name, last_name=last_name).first()

        if user and contact:
            existing = Relationship.query.filter_by(
                entity1_type="user", entity1_id=user.id, entity2_type="contact", entity2_id=contact.id
            ).first()

            if not existing:
                relationship = Relationship.create_relationship(
                    entity1_type="user", entity1_id=user.id, entity2_type="contact", entity2_id=contact.id, relationship_type=rel_type
                )
                db.session.add(relationship)
                logger.info(f"Created relationship: User {user.username} {rel_type} Contact {contact.first_name} {contact.last_name}")

    # Create user-to-company relationships
    company_relationships = [
        ("morgan", "Nimbus Financial", "Account Owner"),
        ("taylor", "Velocity Healthcare Systems", "Account Owner"),
        ("jordan", "GlobalTech Retail", "Technical Lead"),
        ("alex", "Quantum Innovations", "Solution Architect"),
        ("casey", "Meridian Energy", "Account Owner"),
        ("morgan", "Axion Logistics", "Executive Sponsor"),
        ("taylor", "Horizon Media Group", "Account Owner"),
    ]

    for username, company_name, rel_type in company_relationships:
        user = User.query.filter_by(username=username).first()
        company = Company.query.filter_by(name=company_name).first()

        if user and company:
            existing = Relationship.query.filter_by(
                entity1_type="user", entity1_id=user.id, entity2_type="company", entity2_id=company.id
            ).first()

            if not existing:
                relationship = Relationship.create_relationship(
                    entity1_type="user", entity1_id=user.id, entity2_type="company", entity2_id=company.id, relationship_type=rel_type
                )
                db.session.add(relationship)
                logger.info(f"Created relationship: User {user.username} {rel_type} Company {company.name}")

    safe_commit()
    logger.info("✅ Relationships seeded.")
