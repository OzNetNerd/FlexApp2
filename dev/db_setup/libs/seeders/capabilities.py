# seeders/capabilities.py - Capabilities seeder

import logging

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit
from libs.seed_data import CAPABILITY_MAP, COMPANY_CAPABILITY_MAP

# Setup paths
root_dir, _ = setup_paths()

from app.models import Capability, CapabilityCategory, Company, CompanyCapability

logger = logging.getLogger(__name__)


def seed_capabilities_and_categories():
    """Seed capabilities and categories into the database."""
    categories = ["Cloud Security", "DevSecOps", "Compliance", "Identity", "Network Security"]
    for category in categories:
        create_or_update(CapabilityCategory, {"name": category}, {})
    safe_commit()

    for category_name, capability_names in CAPABILITY_MAP.items():
        category = CapabilityCategory.query.filter_by(name=category_name).first()
        for cap_name in capability_names:
            create_or_update(Capability, {"name": cap_name}, {"category": category})
    safe_commit()
    logger.info("✅ Capabilities and categories seeded.")


def seed_company_capabilities():
    """Seed company capabilities into the database."""
    companies = Company.query.all()
    capabilities = Capability.query.all()

    for company_name, capability_names in COMPANY_CAPABILITY_MAP.items():
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

    safe_commit()
    logger.info("✅ CompanyCapabilities seeded.")
