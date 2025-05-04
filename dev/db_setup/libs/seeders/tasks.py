# seeders/tasks.py - Task seeder

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from libs.path_utils import setup_paths
from libs.seed_utils import create_or_update, safe_commit

# Setup paths
root_dir, _ = setup_paths()

from app.models.pages.task import Task
from app.models.pages.user import User
from app.models.pages.opportunity import Opportunity

logger = logging.getLogger(__name__)


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
            "assigned_to_id": user.id,
            "completed_at": completed_at
        }

        create_or_update(Task, {"title": title}, task_data)

    safe_commit()
    logger.info("✅ Tasks seeded.")