# seeders/srs.py - SRS items seeder

import logging

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models.pages.srs import SRS

logger = logging.getLogger(__name__)

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

    safe_commit()
    logger.info("✅ SRS items seeded.")