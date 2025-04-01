from app.routes.base.components.entity_handler import Tab, TabSection, TabEntry
from typing import List
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


def get_contact_tabs(item: dict) -> List[Tab]:
    """Returns the list of contact-related tabs with data populated from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    logger.info(f"Building contact tabs with input item")
    logger.debug(f"Input item: {item}")

    # --- Basic Info Tab ---


    basic_info_tab_name = "Basic Info"
    logger.info(f"Creating {basic_info_tab_name} tab")
    contact_session_name = "Contact"
    contact_info_section = TabSection(
        section_name=contact_session_name,
        entries=[
            TabEntry(entry_name="first_name", label="First Name", type="text", required=True,
                     value=item.get("first_name")),
            TabEntry(entry_name="last_name", label="Last Name", type="text", required=True,
                     value=item.get("last_name")),
            TabEntry(entry_name="email", label="Email", type="email", required=True, value=item.get("email")),
            TabEntry(entry_name="phone_number", label="Phone Number", type="text", value=item.get("phone_number")),
        ]
    )
    logger.info(f"Finished creating {contact_session_name} section")

    role_info_section_name = "Role Information"
    role_info_section = TabSection(
        section_name=role_info_section_name,
        entries=[
            TabEntry(entry_name="role", label="Role", type="text", value=item.get("role")),
            TabEntry(
                entry_name="role_level",
                label="Role Level",
                type="dropdown",
                options=["Junior", "Mid", "Senior", "Lead"],
                value=item.get("role_level")
            ),
            TabEntry(entry_name="team_bu_name", label="Team Name", type="text", value=item.get("team_bu_name")),
        ]
    )
    logger.info(f"Finished creating {role_info_section_name} section")

    basic_info_tab = Tab(tab_name=basic_info_tab_name, sections=[contact_info_section, role_info_section])
    logger.debug(f"Created {basic_info_tab_name}")

    # --- Role & Responsibilities Tab ---
    roles_responsibilities_tab_name = "Role and Responsibilities"
    roles_responsibilities_section_name = "Role and Responsibilities"
    logger.info(f"Creating {roles_responsibilities_tab_name} tab")
    role_responsibilities_section = TabSection(
        section_name=roles_responsibilities_tab_name,
        entries=[
            TabEntry(
                entry_name="team_roles_responsibilities",
                label="Team's Roles and Responsibilities",
                type="textarea",
                value=item.get("team_roles_responsibilities")
            ),
            TabEntry(
                entry_name="role_description",
                label="Role Description",
                type="textarea",
                value=item.get("role_description")
            ),
            TabEntry(
                entry_name="responsibilities",
                label="Responsibilities",
                type="textarea",
                value=item.get("responsibilities")
            ),
        ]
    )
    logger.debug(f"Created {roles_responsibilities_section_name} section: {role_responsibilities_section}")

    role_tab = Tab(tab_name=roles_responsibilities_tab_name, sections=[role_responsibilities_section])
    logger.debug(f"Created Role and Responsibilities tab: {role_tab}")

    # --- Skills & Technologies Tab ---
    skills_technologies_tab_name = "Skills & Technologies tab"
    skills_level_section_name = "Skill Level"
    logger.info(f"Creating {skills_technologies_tab_name} tab")
    skill_level_section = TabSection(
        section_name=skills_level_section_name,
        entries=[
            TabEntry(
                entry_name="primary_skill_area",
                label="Primary Skill Area",
                type="dropdown",
                options=["Cloud", "DevOps", "Networking", "Programming", "Security"],
                value=item.get("primary_skill_area")
            ),
            TabEntry(
                entry_name="skill_level",
                label="Skill Level",
                type="dropdown",
                options=["Beginner", "Intermediate", "Advanced", "Expert"],
                value=item.get("skill_level")
            ),
            TabEntry(
                entry_name="certifications",
                label="Certifications",
                type="textarea",
                value=item.get("certifications")
            ),
        ]
    )
    logger.debug(f"Created {skills_level_section_name} section: {skill_level_section}")

    technologies_used_section_name = "Technologies Used"
    technologies_used_section = TabSection(
        section_name=technologies_used_section_name,
        entries=[
            TabEntry(
                entry_name="cloud_platforms",
                label="Cloud Platforms",
                type="dropdown",
                options=["AWS", "Azure", "Google Cloud", "IBM Cloud"],
                value=item.get("cloud_platforms")
            ),
            TabEntry(
                entry_name="devops_tools",
                label="DevOps Tools",
                type="dropdown",
                options=["Terraform", "Jenkins", "Ansible", "Docker", "Kubernetes"],
                value=item.get("devops_tools")
            ),
            TabEntry(
                entry_name="version_control_systems",
                label="Version Control Systems",
                type="dropdown",
                options=["Git", "SVN", "Mercurial"],
                value=item.get("version_control_systems")
            ),
            TabEntry(
                entry_name="programming_languages",
                label="Programming Languages",
                type="dropdown",
                options=["Python", "JavaScript", "Java", "Go", "Ruby"],
                value=item.get("programming_languages")
            ),
            TabEntry(
                entry_name="monitoring_logging",
                label="Monitoring & Logging",
                type="dropdown",
                options=["Prometheus", "Grafana", "Splunk", "ELK Stack"],
                value=item.get("monitoring_logging")
            ),
            TabEntry(
                entry_name="ci_cd_tools",
                label="CI/CD Tools",
                type="dropdown",
                options=["GitLab CI", "CircleCI", "Travis CI", "Azure DevOps"],
                value=item.get("ci_cd_tools")
            ),
            TabEntry(
                entry_name="other_technologies",
                label="Other Technologies",
                type="textarea",
                value=item.get("other_technologies")
            ),
        ]
    )
    logger.debug(f"Created {technologies_used_section_name} section: {technologies_used_section}")

    skills_tab = Tab(tab_name=skills_technologies_tab_name, sections=[skill_level_section, technologies_used_section])
    logger.debug(f"Created Skills and Technologies tab: {skills_tab}")

    # --- Expertise & Projects Tab ---
    expertise_projects_tab_name = "Expertise & Projects"
    expertise_projects_section_name = "Expertise and Projects"
    logger.info(f"Creating  tab")
    expertise_section = TabSection(
        section_name=expertise_projects_section_name,
        entries=[
            TabEntry(
                entry_name="expertise_areas",
                label="Expertise Areas",
                type="text",
                value=item.get("expertise_areas")
            ),
            TabEntry(
                entry_name="technologies_led",
                label="Technologies Led/Worked With",
                type="textarea",
                value=item.get("technologies_led")
            ),
        ]
    )
    logger.debug(f"Created {expertise_projects_section_name} section: {expertise_section}")

    expertise_tab = Tab(tab_name=expertise_projects_tab_name, sections=[expertise_section])
    logger.debug(f"Created {expertise_projects_tab_name} tab: {expertise_tab}")

    # --- Metadata Tab ---
    logger.info(f"Creating Metadata tab")
    metadata_section = TabSection(
        section_name="Metadata",
        entries=[
            TabEntry(entry_name="created_at", label="Created At", type="readonly", value=item.get("created_at")),
            TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=item.get("updated_at")),
        ]
    )
    logger.debug(f"Created Metadata section: {metadata_section}")

    metadata_tab = Tab(tab_name="Metadata", sections=[metadata_section])
    logger.debug(f"Created Metadata tab: {metadata_tab}")

    tabs = [basic_info_tab, role_tab, skills_tab, expertise_tab, metadata_tab]
    logger.info(f"Returning {len(tabs)} tabs for contact")
    return tabs