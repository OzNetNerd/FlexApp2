#!/usr/bin/env python
# db_setup.py - Combined database creation and seeding script

import os
import sys
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the models directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Capability, CapabilityCategory, Company, CompanyCapability, Contact, Note, Opportunity, Task, \
    User, db
from app.models.relationship import Relationship
from app.models.pages.srs import SRS


# Setup database connection
def setup_db():
    """Setup the database connection without using Flask"""
    # Use crm.db in the current directory
    db_path = "sqlite:///crm.db"
    logger.info(f"Initializing database at: {db_path}")

    # Check if database file exists
    db_file = "crm.db"
    db_exists = os.path.exists(db_file)

    if not db_exists:
        logger.info("Creating new database...")
    else:
        logger.info("Database already exists, updating as needed...")

    # Create engine and session
    engine = create_engine(db_path)
    db.Model.metadata.create_all(engine)

    # Create a session
    session = scoped_session(sessionmaker(bind=engine))
    db.session = session

    return db_file


def create_or_update(model, match_by: dict, data: dict):
    """Create or update an instance of the model based on the match criteria."""
    instance = model.query.filter_by(**match_by).first()
    if instance:
        # Update the instance with new data
        for key, value in data.items():
            setattr(instance, key, value)
        logger.info(f"Updated existing {model.__name__}: {match_by}")
    else:
        # Create a new instance if none found
        instance = model(**{**match_by, **data})
        db.session.add(instance)
        logger.info(f"Created new {model.__name__}: {match_by}")
    return instance


def seed_users():
    """Seed users into the database."""
    users = [
        ("alice", "Alice Johnson", "alice@example.com", False),
        ("bob", "Bob Smith", "bob@example.com", False),
        ("carol", "Carol White", "carol@example.com", False),
        ("dave", "Dave Black", "dave@example.com", False),
        ("eve", "Eve Grey", "eve@example.com", False),
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
    db.session.commit()
    logger.info("✅ Users seeded.")


def seed_companies():
    """Seed companies into the database."""
    companies = [
        ("FlexTech", "A flexible software consultancy."),
        ("CloudCorp", "Leaders in scalable cloud infrastructure."),
        ("DataSolve", "Data-driven business intelligence solutions."),
        ("CyberTrust", "Next-gen cybersecurity solutions."),
        ("GreenGrid", "Sustainable smart grid technology provider."),
        ("Acme Inc", "Technology company"),
        ("Beta Corp", "Manufacturing company"),
    ]

    for name, description in companies:
        create_or_update(Company, {"name": name}, {"description": description})
    db.session.commit()
    logger.info("✅ Companies seeded.")


def seed_contacts():
    """Seed contacts into the database."""
    companies = Company.query.all()
    contacts_data = [
        # Assigned to companies dynamically
        ("Liam", "Walker", None, "0400012345"),
        ("Noah", "Lee", None, "0400112345"),
        ("Olivia", "Davis", None, "0400212345"),
        ("Emma", "Martin", None, "0400312345"),
        ("Ava", "Lopez", None, "0400412345"),
        # Pre-assigned IDs
        ("Test", "User", 1, None),
        ("Test2", "User2", 2, None),
    ]

    for i, (first_name, last_name, contact_id, phone) in enumerate(contacts_data):
        # For the first 5 contacts, assign to companies dynamically
        if i < 5:
            company = companies[i % len(companies)]
            email = f"{first_name.lower()}@{company.name.lower().replace(' ', '')}.com"
            create_or_update(
                Contact,
                {"first_name": first_name, "last_name": last_name},
                {
                    "phone_number": phone,
                    "email": email,
                    "company": company,
                },
            )
        # For the last 2 contacts with pre-assigned IDs
        else:
            existing = Contact.query.filter_by(id=contact_id).first()
            if not existing:
                contact = Contact(id=contact_id, first_name=first_name, last_name=last_name)
                db.session.add(contact)
                logger.info(f"Created contact with ID {contact_id}: {first_name} {last_name}")

    db.session.commit()
    logger.info("✅ Contacts seeded.")


def seed_capabilities_and_categories():
    """Seed capabilities and categories into the database."""
    categories = ["Security", "Data", "Infrastructure", "DevOps", "AI"]
    for category in categories:
        create_or_update(CapabilityCategory, {"name": category}, {})
    db.session.commit()

    capability_map = {
        "Security": ["Penetration Testing", "Risk Assessment"],
        "Data": ["ETL", "Data Warehousing"],
        "Infrastructure": ["Load Balancing"],
        "DevOps": ["CI/CD Pipelines"],
        "AI": ["ML Model Training"],
    }

    for category_name, capability_names in capability_map.items():
        category = CapabilityCategory.query.filter_by(name=category_name).first()
        for cap_name in capability_names:
            create_or_update(Capability, {"name": cap_name}, {"category": category})
    db.session.commit()
    logger.info("✅ Capabilities and categories seeded.")


def seed_company_capabilities():
    """Seed company capabilities into the database."""
    companies = Company.query.all()
    capabilities = Capability.query.all()

    for i, company in enumerate(companies):
        cap = capabilities[i % len(capabilities)]
        existing = CompanyCapability.query.filter_by(company_id=company.id, capability_id=cap.id).first()
        if not existing:
            db.session.add(CompanyCapability(company=company, capability=cap))
    db.session.commit()
    logger.info("✅ CompanyCapabilities seeded.")


def seed_opportunities():
    """Seed opportunities into the database."""
    companies = Company.query.all()

    opportunities_data = [
        # Dynamic company assignment
        ("Cloud Expansion", "Opportunity to expand our cloud services.", "New", "Prospecting", 50000.0, None),
        ("Security Partnership", "Partnership with a major security firm.", "New", "Prospecting", 100000.0, None),
        ("Data Analytics Project", "Project for a large data analytics firm.", "Won", "Negotiation", 150000.0, None),
        ("Software Licensing", "Renewal of software licenses for an enterprise.", "Lost", "Closed", 30000.0, None),
        ("Cybersecurity Solutions", "Comprehensive cybersecurity solutions for a client.", "New", "Prospecting",
         200000.0, None),
        # Fixed company assignment
        ("New Website", "Build a new website", "New", "Prospecting", 10000.0, 1),
        ("Software Upgrade", "Upgrade ERP system", "In Progress", "Negotiation", 25000.0, 2),
    ]

    for name, description, status, stage, value, company_id in opportunities_data:
        # If company_id is specified, use it; otherwise, select a company using a consistent method
        if company_id is None:
            company_id = companies[len(opportunities_data) % len(companies)].id

        create_or_update(
            Opportunity,
            {"name": name},
            {
                "description": description,
                "status": status,
                "stage": stage,
                "value": value,
                "company_id": company_id,
            },
        )
    db.session.commit()
    logger.info("✅ Opportunities seeded.")


def seed_tasks():
    """Seed tasks into the database."""
    users = User.query.all()
    opportunities = Opportunity.query.all()

    if len(users) == 0 or len(opportunities) == 0:
        logger.warning("❌ Not enough users or opportunities to create tasks.")
        return

    tasks = [
        (
            "Follow up on Cloud Expansion",
            "Follow up with the client about the cloud expansion opportunity.",
            "2025-06-30",
            "Pending",
            "High",
            "Opportunity",
            opportunities[0].id,
        ),
        (
            "Review security partnership terms",
            "Review the proposed terms for the security partnership.",
            "2025-05-15",
            "In Progress",
            "Medium",
            "Opportunity",
            opportunities[1].id,
        ),
        (
            "Prepare proposal for data analytics",
            "Prepare a detailed proposal for the data analytics project.",
            "2025-04-20",
            "Pending",
            "High",
            "Opportunity",
            opportunities[2].id,
        ),
        (
            "Renew software licenses",
            "Process the renewal for software licenses for the enterprise.",
            "2025-07-10",
            "Completed",
            "Low",
            "Opportunity",
            opportunities[3].id,
        ),
        (
            "Cybersecurity audit for client",
            "Complete the cybersecurity audit for the client and report findings.",
            "2025-06-05",
            "Pending",
            "High",
            "Opportunity",
            opportunities[4].id,
        ),
        (
            "User feedback analysis",
            "Analyze user feedback on the latest release.",
            "2025-05-01",
            "Pending",
            "Medium",
            "User",
            users[0].id,
        ),
        (
            "Internal team meeting",
            "Schedule an internal team meeting for next week.",
            "2025-04-25",
            "Completed",
            "Low",
            "User",
            users[1].id,
        ),
    ]

    task_assignments = min(len(users), len(opportunities))

    for i in range(task_assignments):
        title, description, due_date, status, priority, notable_type, notable_id = tasks[i]
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
        create_or_update(
            Task,
            {"title": title},
            {
                "description": description,
                "due_date": due_date,
                "status": status,
                "priority": priority,
                "notable_type": notable_type,
                "notable_id": notable_id,
            },
        )
    db.session.commit()
    logger.info("✅ Tasks seeded.")


def seed_notes():
    """Seed notes for Companies, Contacts, and Opportunities."""
    user = User.query.first()
    if not user:
        logger.warning("❌ No user available to assign notes.")
        return

    # Seed notes for companies
    for company in Company.query.all():
        create_or_update(
            Note,
            {"notable_type": "Company", "notable_id": company.id, "user_id": user.id},
            {"content": f"Note for company {company.name}",
             "processed_content": f"<p>Note for company {company.name}</p>"},
        )

    # Seed notes for contacts
    for contact in Contact.query.all():
        full_name = f"{contact.first_name} {contact.last_name}"
        create_or_update(
            Note,
            {"notable_type": "Contact", "notable_id": contact.id, "user_id": user.id},
            {"content": f"Note for contact {full_name}", "processed_content": f"<p>Note for contact {full_name}</p>"},
        )

    # Seed notes for opportunities
    for opportunity in Opportunity.query.all():
        create_or_update(
            Note,
            {"notable_type": "Opportunity", "notable_id": opportunity.id, "user_id": user.id},
            {"content": f"Note for opportunity {opportunity.name}",
             "processed_content": f"<p>Note for opportunity {opportunity.name}</p>"},
        )
    db.session.commit()
    logger.info("✅ Notes seeded.")


def seed_relationships():
    """Seed relationships between entities in the database."""
    users = User.query.all()
    contacts = Contact.query.all()
    companies = Company.query.all()

    # Define some relationship types
    relationship_types = ["Manages", "Works With", "Reports To", "Client", "Partner", "Vendor"]

    # Create user-to-user relationships
    for i in range(len(users) - 1):
        user1 = users[i]
        user2 = users[i + 1]
        rel_type = relationship_types[i % len(relationship_types)]

        existing = Relationship.query.filter_by(entity1_type="user", entity1_id=user1.id, entity2_type="user",
                                                entity2_id=user2.id).first()

        if not existing:
            relationship = Relationship.create_relationship(
                entity1_type="user", entity1_id=user1.id, entity2_type="user", entity2_id=user2.id,
                relationship_type=rel_type
            )
            db.session.add(relationship)
            logger.info(f"Created relationship: User {user1.username} {rel_type} User {user2.username}")

    # Create user-to-contact relationships
    for i in range(min(len(users), len(contacts))):
        user = users[i]
        contact = contacts[i]
        rel_type = relationship_types[(i + 2) % len(relationship_types)]

        existing = Relationship.query.filter_by(
            entity1_type="user", entity1_id=user.id, entity2_type="contact", entity2_id=contact.id
        ).first()

        if not existing:
            relationship = Relationship.create_relationship(
                entity1_type="user", entity1_id=user.id, entity2_type="contact", entity2_id=contact.id,
                relationship_type=rel_type
            )
            db.session.add(relationship)
            logger.info(
                f"Created relationship: User {user.username} {rel_type} Contact {contact.first_name} {contact.last_name}")

    # Create user-to-company relationships
    for i in range(min(len(users), len(companies))):
        user = users[i]
        company = companies[i]
        rel_type = relationship_types[(i + 4) % len(relationship_types)]

        existing = Relationship.query.filter_by(
            entity1_type="user", entity1_id=user.id, entity2_type="company", entity2_id=company.id
        ).first()

        if not existing:
            relationship = Relationship.create_relationship(
                entity1_type="user", entity1_id=user.id, entity2_type="company", entity2_id=company.id,
                relationship_type=rel_type
            )
            db.session.add(relationship)
            logger.info(f"Created relationship: User {user.username} {rel_type} Company {company.name}")

    db.session.commit()
    logger.info("✅ Relationships seeded.")


def seed_srs_items():
    """Seed SRS items for learning and recall."""
    logger.info("Processing SRS cards...")
    sample_cards = [
        # Contact cards
        {"notable_type": "Contact", "notable_id": 1, "question": "What is Test User's last name?", "answer": "User"},
        {"notable_type": "Contact", "notable_id": 2, "question": "What is Test2 User2's first name?",
         "answer": "Test2"},
        {"notable_type": "Contact", "notable_id": 1, "question": "Which contact has ID #1?", "answer": "Test User"},
        # Company cards
        {"notable_type": "Company", "notable_id": 1, "question": "What industry is Acme Inc in?",
         "answer": "Technology company"},
        {"notable_type": "Company", "notable_id": 2, "question": "What is Beta Corp's main business?",
         "answer": "Manufacturing company"},
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

    for card_data in sample_cards:
        create_or_update(
            SRS,
            {
                "notable_type": card_data["notable_type"],
                "notable_id": card_data["notable_id"],
                "question": card_data["question"]
            },
            {"answer": card_data["answer"]}
        )

    db.session.commit()
    logger.info("✅ SRS items seeded.")


def seed_demo_data():
    """Seed all demo data into the database."""
    entries = [
        seed_users,
        seed_companies,
        seed_contacts,
        seed_capabilities_and_categories,
        seed_company_capabilities,
        seed_opportunities,
        seed_tasks,
        seed_notes,
        seed_relationships,
        seed_srs_items,
    ]

    for entry in entries:
        entry_name = entry.__name__
        logger.info(f"Seeding entry {entry_name}")
        try:
            entry()  # Call the seed function
            logger.info(f"🎉 {entry_name} Done")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"❌ {entry_name} IntegrityError: {e}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ {entry_name} Error seeding data: {e}")


if __name__ == "__main__":
    db_file = setup_db()
    seed_demo_data()
    logger.info(f"✅ Database setup complete: {db_file}")