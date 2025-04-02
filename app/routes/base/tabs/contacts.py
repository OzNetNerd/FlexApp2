from app.routes.base.components.tab_builder import TabSection, TabEntry, TabBuilder
from dataclasses import dataclass, field
from typing import Any, List, Callable
import logging

logger = logging.getLogger(__name__)


@dataclass
class BasicInfoTab(TabBuilder):
    item: Any
    tab_name: str = "Basic Info"

    def _basic_info_section(self):
        section_name = "Contact"
        contact_info_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="first_name", label="First Name", type="text", required=True,
                         value=self.item.get("first_name")),
                TabEntry(entry_name="last_name", label="Last Name", type="text", required=True,
                         value=self.item.get("last_name")),
                TabEntry(entry_name="email", label="Email", type="email", required=True, value=self.item.get("email")),
                TabEntry(entry_name="phone_number", label="Phone Number", type="text", value=self.item.get("phone_number")),
            ]
        )
        logger.info(f"Finished creating {contact_info_section} section")
        return contact_info_section

    def _role_info_section(self):
        section_name = "Role Information"
        role_info_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="role", label="Role", type="text", value=self.item.get("role")),
                TabEntry(
                    entry_name="role_level",
                    label="Role Level",
                    type="dropdown",
                    options=["Junior", "Mid", "Senior", "Lead"],
                    value=self.item.get("role_level")
                ),
                TabEntry(entry_name="team_bu_name", label="Team Name", type="text", value=self.item.get("team_bu_name")),
            ]
        )
        return role_info_section


@dataclass
class RoleAndResponsibilitiesTab(TabBuilder):
    item: Any
    tab_name: str = "Roles and Responsibilities"

    def _role_responsibilities_section(self):
        section_name = "Role and Responsibilities"
        role_responsibilities_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="team_roles_responsibilities",
                    label="Team's Roles and Responsibilities",
                    type="textarea",
                    value=self.item.get("team_roles_responsibilities")
                ),
                TabEntry(
                    entry_name="role_description",
                    label="Role Description",
                    type="textarea",
                    value=self.item.get("role_description")
                ),
                TabEntry(
                    entry_name="responsibilities",
                    label="Responsibilities",
                    type="textarea",
                    value=self.item.get("responsibilities")
                ),
            ]
        )
        return role_responsibilities_section


@dataclass
class SkillsAndTechnologiesTab(TabBuilder):
    item: Any
    tab_name: str = "Skills and Technologies"
    section_method_order: List[Callable] = field(init=False)

    def __post_init__(self):
        self.section_method_order = [
            self._skill_level_section,
            self._technologies_used_section,
        ]

    def _skill_level_section(self):
        section_name = "Skill Level"
        skill_level_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="primary_skill_area",
                    label="Primary Skill Area",
                    type="dropdown",
                    options=["Cloud", "DevOps", "Networking", "Programming", "Security"],
                    value=self.item.get("primary_skill_area")
                ),
                TabEntry(
                    entry_name="skill_level",
                    label="Skill Level",
                    type="dropdown",
                    options=["Beginner", "Intermediate", "Advanced", "Expert"],
                    value=self.item.get("skill_level")
                ),
                TabEntry(
                    entry_name="certifications",
                    label="Certifications",
                    type="textarea",
                    value=self.item.get("certifications")
                ),
            ]
        )
        logger.debug(f"Created {skill_level_section} section")
        return skill_level_section

    def _technologies_used_section(self):
        section_name = "Technologies Used"
        technologies_used_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="cloud_platforms",
                    label="Cloud Platforms",
                    type="dropdown",
                    options=["AWS", "Azure", "Google Cloud", "IBM Cloud"],
                    value=self.item.get("cloud_platforms")
                ),
                TabEntry(
                    entry_name="devops_tools",
                    label="DevOps Tools",
                    type="dropdown",
                    options=["Terraform", "Jenkins", "Ansible", "Docker", "Kubernetes"],
                    value=self.item.get("devops_tools")
                ),
                TabEntry(
                    entry_name="version_control_systems",
                    label="Version Control Systems",
                    type="dropdown",
                    options=["Git", "SVN", "Mercurial"],
                    value=self.item.get("version_control_systems")
                ),
                TabEntry(
                    entry_name="programming_languages",
                    label="Programming Languages",
                    type="dropdown",
                    options=["Python", "JavaScript", "Java", "Go", "Ruby"],
                    value=self.item.get("programming_languages")
                ),
                TabEntry(
                    entry_name="monitoring_logging",
                    label="Monitoring & Logging",
                    type="dropdown",
                    options=["Prometheus", "Grafana", "Splunk", "ELK Stack"],
                    value=self.item.get("monitoring_logging")
                ),
                TabEntry(
                    entry_name="ci_cd_tools",
                    label="CI/CD Tools",
                    type="dropdown",
                    options=["GitLab CI", "CircleCI", "Travis CI", "Azure DevOps"],
                    value=self.item.get("ci_cd_tools")
                ),
                TabEntry(
                    entry_name="other_technologies",
                    label="Other Technologies",
                    type="textarea",
                    value=self.item.get("other_technologies")
                ),
            ]
        )
        return technologies_used_section

@dataclass
class ExpertiseAndProjectsTab(TabBuilder):
    item: Any
    tab_name: str = "Expertise and Projects"

    def __post_init__(self):
        self.section_method_order = [
            self._expertise_section,
        ]

    def _expertise_section(self):
        section_name = "Expertise and Projects"
        expertise_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="expertise_areas",
                    label="Expertise Areas",
                    type="text",
                    value=self.item.get("expertise_areas")
                ),
                TabEntry(
                    entry_name="technologies_led",
                    label="Technologies Led/Worked With",
                    type="textarea",
                    value=self.item.get("technologies_led")
                ),
            ]
        )
        return expertise_section

def contacts_tabs(item):
    tabs = []

    for tab in [BasicInfoTab, RoleAndResponsibilitiesTab, SkillsAndTechnologiesTab, ExpertiseAndProjectsTab]:
        tabs.append(tab.create_tab(item))

    return tabs
