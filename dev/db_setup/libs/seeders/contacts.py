# seeders/contacts.py - Contact seeder

import logging

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models import Contact, Company

logger = logging.getLogger(__name__)


def seed_contacts():
    """Seed contacts into the database."""
    companies = Company.query.all()
    contacts_data = [
        # Assigned to companies dynamically
        ("James", "Wilson", None, "415-555-9876", "CISO"),
        ("Sarah", "Martinez", None, "212-555-7832", "Cloud Security Architect"),
        ("Michael", "Thompson", None, "650-555-3214", "DevSecOps Lead"),
        ("Emily", "Johnson", None, "312-555-8765", "CTO"),
        ("David", "Patel", None, "408-555-2398", "VP of Infrastructure"),
        ("Jennifer", "Garcia", None, "206-555-4567", "Cloud Operations Manager"),
        ("Robert", "Kim", None, "617-555-8901", "Security Operations Director"),
        # Pre-assigned IDs
        ("Priya", "Sharma", 1, "202-555-1234", "Director of Cloud Transformation"),
        ("Daniel", "Roberts", 2, "512-555-5678", "CISO"),
    ]

    for i, (first_name, last_name, contact_id, phone, role_title) in enumerate(contacts_data):
        # For the first 7 contacts, assign to companies dynamically
        if i < 7:
            company = companies[i % len(companies)]
            email = f"{first_name.lower()}.{last_name.lower()}@{company.name.lower().replace(' ', '')}.com"
            create_or_update(
                Contact,
                {"first_name": first_name, "last_name": last_name},
                {
                    "phone_number": phone,
                    "email": email,
                    "company": company,
                    "role": role_title,
                },
            )
        # For the last 2 contacts with pre-assigned IDs
        else:
            existing = Contact.query.filter_by(id=contact_id).first()
            if not existing:
                company = companies[contact_id % len(companies)]
                email = f"{first_name.lower()}.{last_name.lower()}@{company.name.lower().replace(' ', '')}.com"
                contact = Contact(
                    id=contact_id,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone,
                    email=email,
                    role=role_title,
                    company=company,
                )
                db.session.add(contact)
                logger.info(f"Created contact with ID {contact_id}: {first_name} {last_name}")

    safe_commit()
    logger.info("✅ Contacts seeded.")
