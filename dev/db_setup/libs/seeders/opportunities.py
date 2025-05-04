# seeders/opportunities.py - Opportunity seeder

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models import Company, Opportunity, User  # Add User import

logger = logging.getLogger(__name__)


def seed_opportunities():
    """Seed opportunities into the database."""
    companies = Company.query.all()

    # Get admin user or default to ID 1
    admin_user = User.query.filter_by(is_admin=True).first() or User.query.get(1)
    if not admin_user:
        logger.warning("No admin user found for opportunities. Using None for created_by_id.")

    created_by_id = admin_user.id if admin_user else None

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
                "created_by_id": created_by_id,  # Add the new field
            },
        )
    safe_commit()
    logger.info("✅ Opportunities seeded.")