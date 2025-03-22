from models import db
from models.company import Company
from models.capability import Capability
from models.company_capability import CompanyCapability
import logging

logger = logging.getLogger(__name__)


def link_capability_to_company(company_id: int, capability_id: int) -> str:
    """Link a capability to a company if it is not already linked."""
    logger.debug(f"Linking capability {capability_id} to company {company_id}")

    if not Company.query.get(company_id):
        logger.warning(f"Company {company_id} not found.")
        return "Company not found."

    if not Capability.query.get(capability_id):
        logger.warning(f"Capability {capability_id} not found.")
        return "Capability not found."

    existing = CompanyCapability.query.filter_by(
        company_id=company_id, capability_id=capability_id
    ).first()

    if existing:
        logger.info(f"Capability {capability_id} already linked to company {company_id}.")
        return "Already linked."

    link = CompanyCapability(company_id=company_id, capability_id=capability_id)
    db.session.add(link)
    db.session.commit()
    logger.info(f"Linked capability {capability_id} to company {company_id}.")
    return "Capability linked."


def unlink_capability_from_company(company_id: int, capability_id: int) -> str:
    """Unlink a capability from a company."""
    logger.debug(f"Unlinking capability {capability_id} from company {company_id}")

    link = CompanyCapability.query.filter_by(
        company_id=company_id, capability_id=capability_id
    ).first()

    if not link:
        logger.warning(f"No link found between company {company_id} and capability {capability_id}.")
        return "Link does not exist."

    db.session.delete(link)
    db.session.commit()
    logger.info(f"Unlinked capability {capability_id} from company {company_id}.")
    return "Capability unlinked."


def get_capabilities_for_company(company_id: int) -> list[Capability]:
    """Return all Capability objects linked to the given company."""
    logger.debug(f"Fetching capabilities for company {company_id}")
    company = Company.query.get(company_id)
    if not company:
        logger.warning(f"Company {company_id} not found.")
        return []
    return company.capabilities


def get_companies_using_capability(capability_id: int) -> list[Company]:
    """Return all Company objects that use the given capability."""
    logger.debug(f"Fetching companies using capability {capability_id}")
    capability = Capability.query.get(capability_id)
    if not capability:
        logger.warning(f"Capability {capability_id} not found.")
        return []
    return capability.companies
