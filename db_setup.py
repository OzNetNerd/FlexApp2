#!/usr/bin/env python
# db_setup.py - Combined database creation and seeding script

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from datetime import datetime
from zoneinfo import ZoneInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the models directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models import Capability, CapabilityCategory, Company, CompanyCapability, Contact, Note, Opportunity, Task, User, db
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
        # Ensure the database directory exists
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
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
    db.session.commit()
    logger.info("✅ Users seeded.")


def seed_companies():
    """Seed companies into the database."""
    companies = [
        ("Nimbus Financial", "Large financial services company with hybrid cloud environment, primarily AWS and on-prem."),
        ("Velocity Healthcare Systems", "Healthcare provider with growing Azure footprint and strict compliance requirements."),
        ("GlobalTech Retail", "Multi-national retailer operating across GCP, AWS, and Azure with containerized microservices."),
        ("Quantum Innovations", "Fast-growing SaaS provider with cloud-native architecture using Kubernetes across multiple clouds."),
        ("Meridian Energy", "Energy company with critical infrastructure transitioning from on-prem to AWS cloud services."),
        ("Axion Logistics", "Supply chain company with legacy systems and new cloud initiatives creating security visibility gaps."),
        ("Horizon Media Group", "Media company with extensive data analytics workloads running in multi-cloud environment."),
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
                    id=contact_id, first_name=first_name, last_name=last_name, phone_number=phone, email=email, role=role_title, company=company
                )
                db.session.add(contact)
                logger.info(f"Created contact with ID {contact_id}: {first_name} {last_name}")

    db.session.commit()
    logger.info("✅ Contacts seeded.")


def seed_capabilities_and_categories():
    """Seed capabilities and categories into the database."""
    categories = ["Cloud Security", "DevSecOps", "Compliance", "Identity", "Network Security"]
    for category in categories:
        create_or_update(CapabilityCategory, {"name": category}, {})
    db.session.commit()

    capability_map = {
        "Cloud Security": ["CSPM", "CWPP", "Container Security", "Cloud IAM Security", "Cloud Data Security"],
        "DevSecOps": ["Pipeline Security", "IaC Scanning", "Container Registry Scanning", "SBOM Management"],
        "Compliance": ["HIPAA", "PCI-DSS", "SOC2", "GDPR", "ISO27001"],
        "Identity": ["Privileged Access Management", "SSO Integration", "Zero Trust Implementation"],
        "Network Security": ["ZTNA", "Cloud Network Segmentation", "API Security"],
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

    # Create more realistic relationships between companies and capabilities
    company_capability_map = {
        "Nimbus Financial": ["CSPM", "Cloud IAM Security", "Privileged Access Management", "PCI-DSS"],
        "Velocity Healthcare Systems": ["HIPAA", "CSPM", "Cloud Data Security", "ZTNA"],
        "GlobalTech Retail": ["Container Security", "Pipeline Security", "Cloud Network Segmentation"],
        "Quantum Innovations": ["Container Security", "IaC Scanning", "SBOM Management", "API Security"],
        "Meridian Energy": ["CSPM", "CWPP", "SOC2", "SSO Integration"],
        "Axion Logistics": ["CSPM", "Zero Trust Implementation", "Cloud Network Segmentation"],
        "Horizon Media Group": ["Cloud Data Security", "GDPR", "API Security", "Container Registry Scanning"],
    }

    for company_name, capability_names in company_capability_map.items():
        company = Company.query.filter_by(name=company_name).first()
        if not company:
            continue

        for cap_name in capability_names:
            capability = Capability.query.filter_by(name=cap_name).first()
            if not capability:
                continue

            existing = CompanyCapability.query.filter_by(company_id=company.id, capability_id=capability.id).first()
            if not existing:
                db.session.add(CompanyCapability(company=company, capability=capability))

    db.session.commit()
    logger.info("✅ CompanyCapabilities seeded.")


def seed_opportunities():
    """Seed opportunities into the database."""
    companies = Company.query.all()

    # Get current date and future dates for close_date
    now = datetime.now(ZoneInfo("UTC"))
    q3_close = now.replace(month=9, day=30, hour=0, minute=0, second=0, microsecond=0)
    q4_close = now.replace(month=12, day=31, hour=0, minute=0, second=0, microsecond=0)
    next_year_close = now.replace(year=now.year + 1, month=3, day=31, hour=0, minute=0, second=0, microsecond=0)

    opportunities_data = [
        (
            "Prisma Cloud Enterprise Deployment",
            "Full Prisma Cloud platform deployment across multi-cloud environment with CSPM, CWPP, and DSPM modules.",
            "In Progress",
            "Technical Evaluation",
            750000.0,
            "Nimbus Financial",
            "high",
            q3_close,
        ),
        (
            "Healthcare Compliance Automation",
            "Implementation of Prisma Cloud for automated HIPAA compliance reporting and remediation.",
            "New",
            "Proposal",
            350000.0,
            "Velocity Healthcare Systems",
            "medium",
            q3_close,
        ),
        (
            "Container Security Initiative",
            "Securing container deployments across development and production with Prisma Cloud.",
            "Won",
            "Closed Won",
            480000.0,
            "GlobalTech Retail",
            "medium",
            now.replace(month=now.month - 1, day=15),
        ),
        (
            "Cloud Security Posture Assessment",
            "Comprehensive assessment of current cloud security posture with recommendations for improvement.",
            "Lost",
            "Closed Lost",
            120000.0,
            "Quantum Innovations",
            "low",
            now.replace(month=now.month - 2, day=1),
        ),
        (
            "Critical Infrastructure Protection",
            "Securing cloud migration of critical energy infrastructure with Prisma Cloud.",
            "New",
            "Discovery",
            680000.0,
            "Meridian Energy",
            "high",
            q4_close,
        ),
        (
            "Supply Chain Security Transformation",
            "Complete security transformation program for hybrid cloud environment.",
            "In Progress",
            "Negotiation",
            520000.0,
            "Axion Logistics",
            "medium",
            q3_close,
        ),
        (
            "Data Protection and Compliance",
            "Implementing Prisma Cloud Data Security with focus on regulatory compliance.",
            "New",
            "Qualification",
            280000.0,
            "Horizon Media Group",
            "low",
            next_year_close,
        ),
    ]

    for name, description, status, stage, value, company_name, priority, close_date in opportunities_data:
        company = Company.query.filter_by(name=company_name).first()
        if not company:
            continue

        create_or_update(
            Opportunity,
            {"name": name},
            {
                "description": description,
                "status": status,
                "stage": stage,
                "value": value,
                "company_id": company.id,
                "priority": priority,
                "close_date": close_date,
                "last_activity_date": datetime.now(ZoneInfo("UTC")),
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
            "Prepare Prisma Cloud technical demo",
            "Schedule and prepare technical demonstration of Prisma Cloud CSPM and CWPP capabilities.",
            "Pending",
            "High",
            "Opportunity",
            "Prisma Cloud Enterprise Deployment",
            "morgan",
        ),
        (
            "Draft healthcare compliance presentation",
            "Create presentation on how Prisma Cloud automates compliance for HIPAA requirements.",
            "In Progress",
            "Medium",
            "Opportunity",
            "Healthcare Compliance Automation",
            "taylor",
        ),
        (
            "Container security workshop",
            "Conduct hands-on workshop with client DevOps team on container security best practices.",
            "Pending",
            "High",
            "Opportunity",
            "Container Security Initiative",
            "jordan",
        ),
        (
            "Conduct security posture assessment",
            "Complete the cloud security posture assessment and document findings for client presentation.",
            "completed",
            "Medium",
            "Opportunity",
            "Cloud Security Posture Assessment",
            "alex",
        ),
        (
            "Critical infrastructure risk analysis",
            "Analyze potential security risks during cloud migration of critical infrastructure.",
            "Pending",
            "High",
            "Opportunity",
            "Critical Infrastructure Protection",
            "casey",
        ),
        (
            "Update security transformation proposal",
            "Revise proposal based on client feedback and updated requirements.",
            "Pending",
            "Medium",
            "Opportunity",
            "Supply Chain Security Transformation",
            "morgan",
        ),
        (
            "Prepare data compliance requirements document",
            "Document specific regulatory requirements and map to Prisma Cloud capabilities.",
            "Pending",
            "Medium",
            "Opportunity",
            "Data Protection and Compliance",
            "taylor",
        ),
    ]

    for title, description, status, priority, notable_type, opportunity_name, username in tasks:
        # Find the opportunity
        opportunity = next((o for o in opportunities if o.name == opportunity_name), None)
        if not opportunity:
            continue

        # Find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            continue

        # Set due date to 30 days from now in UTC
        due_date = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
        due_date = due_date.replace(day=due_date.day + 30)

        # Set completed_at timestamp if the task is completed
        completed_at = None
        if status == "completed":
            completed_at = datetime.now(ZoneInfo("UTC"))

        task_data = {
            "description": description,
            "due_date": due_date,
            "status": status,
            "priority": priority,
            "notable_type": notable_type,
            "notable_id": opportunity.id,
            "assigned_to_id": user.id,  # Updated to use assigned_to_id instead of assigned_to
            "completed_at": completed_at  # Set the completed_at timestamp for completed tasks
        }

        create_or_update(Task, {"title": title}, task_data)
    db.session.commit()
    logger.info("✅ Tasks seeded.")


def seed_notes():
    """Seed notes for Companies, Contacts, and Opportunities."""
    users = User.query.all()

    if len(users) == 0:
        logger.warning("❌ No user available to assign notes.")
        return

    # Seed notes for companies
    for company in Company.query.all():
        user = users[hash(company.name) % len(users)]

        if company.name == "Nimbus Financial":
            content = "Key customer with large AWS and Azure footprint. Security team is concerned about IAM misconfigurations and over-privileged roles. Looking to consolidate security tools and automate remediation."
        elif company.name == "Velocity Healthcare Systems":
            content = "Struggling with HIPAA compliance in their Azure environment. Their CISO mentioned they had a security incident last quarter related to misconfigured storage containers. Very interested in automated compliance reporting."
        elif company.name == "GlobalTech Retail":
            content = "Recently adopted Kubernetes for their e-commerce platform. Development team moving fast but security team concerned about container vulnerabilities. Need visibility into their container security posture."
        elif company.name == "Quantum Innovations":
            content = "Fast-moving startup with all cloud-native architecture. Security is not their primary focus, but recent customer requirements are pushing them to improve security posture. Price sensitive."
        elif company.name == "Meridian Energy":
            content = "Critical infrastructure provider with strict regulatory requirements. Moving sensitive workloads to AWS and concerned about security during migration. Board-level visibility on security initiatives."
        elif company.name == "Axion Logistics":
            content = "Complex environment with mix of legacy systems and new cloud services. Security team understaffed and looking for ways to automate security processes. Particularly concerned about secure cloud networking."
        elif company.name == "Horizon Media Group":
            content = "Handles large volumes of user data subject to GDPR. Recent expansion of analytics platform across multiple clouds has created security blind spots. Looking for unified security visibility."
        else:
            content = f"Note for company {company.name}"

        create_or_update(
            Note,
            {"notable_type": "Company", "notable_id": company.id, "user_id": user.id},
            {"content": content, "processed_content": f"<p>{content}</p>"},
        )

    # Seed notes for contacts
    for contact in Contact.query.all():
        user = users[hash(contact.email) % len(users)]
        full_name = f"{contact.first_name} {contact.last_name}"

        if contact.role == "CISO":
            content = f"Met with {full_name} during the cloud security summit. Very knowledgeable about cloud security challenges. Primary decision maker for security investments. Concerned about compliance automation and reporting to the board."
        elif "Security" in contact.role:
            content = f"{full_name} is technically focused and wants details on how Prisma Cloud handles container vulnerabilities and IaC scanning. Prefers hands-on demos over slideware. Looking for security that doesn't slow down development."
        elif "CTO" in contact.role:
            content = f"{full_name} is concerned about shadow IT and unmanaged cloud resources. Wants to enable developer velocity while maintaining security. Interested in API integration capabilities of Prisma Cloud."
        elif "Operations" in contact.role:
            content = f"{full_name} manages the cloud operations team. Frustrated with current alert volume and looking for automated remediation. Wants better visibility across multi-cloud environment."
        elif "VP" in contact.role:
            content = f"{full_name} is evaluating consolidation of security tools to reduce costs. Needs executive-level reporting for board meetings. Interested in ROI metrics for security investments."
        elif "Director" in contact.role:
            content = f"{full_name} is leading the cloud transformation initiative. Looking for security that can keep pace with rapid adoption of new cloud services. Wants a partner, not just a vendor."
        else:
            content = f"Note for contact {full_name}"

        create_or_update(
            Note,
            {"notable_type": "Contact", "notable_id": contact.id, "user_id": user.id},
            {"content": content, "processed_content": f"<p>{content}</p>"},
        )

    # Seed notes for opportunities
    for opportunity in Opportunity.query.all():
        user = users[hash(opportunity.name) % len(users)]

        if "Enterprise Deployment" in opportunity.name:
            content = "Multi-phase deployment planned. Initial focus on AWS environment, followed by Azure in Q3. Client concerned about maintaining compliance during rapid cloud expansion. POC showed 70% reduction in cloud misconfigurations."
        elif "Compliance" in opportunity.name:
            content = "Client needs automated compliance reporting for HIPAA. Current manual process takes 2 weeks each quarter. Prisma Cloud demo showed ability to reduce to 2 days with higher accuracy. Technical team convinced, now working on business case."
        elif "Container" in opportunity.name:
            content = "POC results were very positive. Client found 28 critical vulnerabilities in production containers. Now moving to full deployment across all environments. Integration with CI/CD pipeline is key requirement."
        elif "Assessment" in opportunity.name:
            content = "Assessment completed but client decided to delay implementation due to budget constraints. Plan to re-engage next quarter when new fiscal year begins. Keep relationship warm."
        elif "Infrastructure" in opportunity.name:
            content = "High-visibility project with board oversight. Client concerned about securing critical infrastructure during cloud migration. Need to demonstrate compliance with energy sector regulations. Timeline accelerated due to recent incidents."
        elif "Transformation" in opportunity.name:
            content = "Complex multi-year engagement. First phase focused on securing cloud workloads, second phase on Zero Trust implementation. Multiple stakeholders with different priorities. Regular executive briefings required."
        elif "Data Protection" in opportunity.name:
            content = "Initial discovery showed significant data compliance gaps. Client handling PII across multiple cloud environments without consistent controls. Proposal focuses on data classification, encryption, and access monitoring."
        else:
            content = f"Note for opportunity {opportunity.name}"

        create_or_update(
            Note,
            {"notable_type": "Opportunity", "notable_id": opportunity.id, "user_id": user.id},
            {"content": content, "processed_content": f"<p>{content}</p>"},
        )

    db.session.commit()
    logger.info("✅ Notes seeded.")


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

    db.session.commit()
    logger.info("✅ Relationships seeded.")


def seed_srs_items():
    """Seed SRS items for learning and recall about cloud security customers."""
    logger.info("Processing SRS cards...")
    sample_cards = [
        # Contact cards
        {
            "notable_type": "Contact",
            "notable_id": 1,
            "question": "What is Priya Sharma's role at her company?",
            "answer": "Director of Cloud Transformation",
        },
        {"notable_type": "Contact", "notable_id": 2, "question": "What is Daniel Roberts' position?", "answer": "CISO"},
        {"notable_type": "Contact", "notable_id": 1, "question": "Which company does Priya Sharma work for?", "answer": "Nimbus Financial"},
        # Company cards
        {
            "notable_type": "Company",
            "notable_id": 1,
            "question": "What is Nimbus Financial's primary cloud environment?",
            "answer": "Hybrid cloud environment, primarily AWS and on-prem",
        },
        {
            "notable_type": "Company",
            "notable_id": 2,
            "question": "What compliance requirements does Velocity Healthcare Systems have?",
            "answer": "HIPAA compliance with strict requirements",
        },
        {
            "notable_type": "Company",
            "notable_id": 3,
            "question": "What cloud platforms does GlobalTech Retail use?",
            "answer": "GCP, AWS, and Azure with containerized microservices",
        },
        # Opportunity cards
        {
            "notable_type": "Opportunity",
            "notable_id": 1,
            "question": "What is the value of the Prisma Cloud Enterprise Deployment opportunity?",
            "answer": "$750,000",
        },
        {
            "notable_type": "Opportunity",
            "notable_id": 2,
            "question": "What stage is the Healthcare Compliance Automation opportunity in?",
            "answer": "Proposal",
        },
        {
            "notable_type": "Opportunity",
            "notable_id": 3,
            "question": "Which company is associated with the Container Security Initiative opportunity?",
            "answer": "GlobalTech Retail",
        },
        # Cloud security specific cards
        {
            "notable_type": "Company",
            "notable_id": 5,
            "question": "Why is cloud security especially critical for Meridian Energy?",
            "answer": "They are an energy company with critical infrastructure transitioning to AWS cloud services",
        },
        {
            "notable_type": "Company",
            "notable_id": 6,
            "question": "What is Axion Logistics' main security challenge?",
            "answer": "Security visibility gaps between legacy systems and new cloud initiatives",
        },
    ]

    for card_data in sample_cards:
        create_or_update(
            SRS,
            {"notable_type": card_data["notable_type"], "notable_id": card_data["notable_id"], "question": card_data["question"]},
            {"answer": card_data["answer"]},
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