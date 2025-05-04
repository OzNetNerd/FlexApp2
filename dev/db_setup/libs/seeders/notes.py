# seeders/notes.py - Notes seeder

import logging

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models import Note, Company, Contact, Opportunity, User

logger = logging.getLogger(__name__)


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

    safe_commit()
    logger.info("✅ Notes seeded.")
