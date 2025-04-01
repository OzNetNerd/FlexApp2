from app.routes.base.components.form_handler import Tab, TabSection, TabEntry
from typing import List

def get_contact_tabs(item: dict) -> List[Tab]:
    """Returns the list of contact-related tabs with data populated from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # --- Basic Info Tab ---
    contact_info_section = TabSection(
        section_name="Contact Information",
        entries=[
            TabEntry(entry_name="name", label="Name", type="text", required=True, value=item.get("name")),
            TabEntry(entry_name="email", label="Email", type="email", required=True, value=item.get("email")),
            TabEntry(entry_name="phone_number", label="Phone Number", type="text", value=item.get("phone_number")),
        ]
    )
    role_info_section = TabSection(
        section_name="Role Information",
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
    basic_info_tab = Tab(tab_name="Basic Info", sections=[contact_info_section, role_info_section])

    # --- Role & Responsibilities Tab ---
    role_responsibilities_section = TabSection(
        section_name="Role & Responsibilities",
        entries=[
            TabEntry(
                entry_name="team_roles_responsibilities",
                label="Team's Roles & Responsibilities",
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
    role_tab = Tab(tab_name="Role & Responsibilities", sections=[role_responsibilities_section])

    # --- Skills & Technologies Tab ---
    skill_level_section = TabSection(
        section_name="Skill Level",
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
    technologies_used_section = TabSection(
        section_name="Technologies Used",
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
    skills_tab = Tab(tab_name="Skills & Technologies", sections=[skill_level_section, technologies_used_section])

    # --- Expertise & Projects Tab ---
    expertise_section = TabSection(
        section_name="Expertise & Projects",
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
    expertise_tab = Tab(tab_name="Expertise & Projects", sections=[expertise_section])

    # --- Metadata Tab ---
    metadata_section = TabSection(
        section_name="Metadata",
        entries=[
            TabEntry(entry_name="created_at", label="Created At", type="readonly", value=item.get("created_at")),
            TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=item.get("updated_at")),
        ]
    )
    metadata_tab = Tab(tab_name="Metadata", sections=[metadata_section])

    return [basic_info_tab, role_tab, skills_tab, expertise_tab, metadata_tab]
