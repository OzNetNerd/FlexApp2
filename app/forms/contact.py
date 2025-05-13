from .base import BaseModelForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class ContactForm(BaseModelForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=127)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=127)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    phone_number = StringField("Phone Number", validators=[Optional(), Length(max=50)])
    role = StringField("Role", validators=[Optional(), Length(max=255)])
    role_level = SelectField(
        "Role Level",
        choices=[
            ("", "Select Level"),
            ("entry", "Entry Level"),
            ("junior", "Junior"),
            ("mid", "Mid-Level"),
            ("senior", "Senior"),
            ("lead", "Lead"),
            ("manager", "Manager"),
            ("director", "Director"),
            ("executive", "Executive"),
        ],
        validators=[Optional()],
    )

    company_id = SelectField("Company", coerce=int, validators=[Optional()])

    team_roles_responsibilities = TextAreaField("Team Roles & Responsibilities")
    role_description = TextAreaField("Role Description")
    responsibilities = TextAreaField("Responsibilities")

    primary_skill_area = SelectField(
        "Primary Skill Area",
        choices=[
            ("", "Select Skill Area"),
            ("cloud", "Cloud"),
            ("devops", "DevOps"),
            ("development", "Development"),
            ("security", "Security"),
            ("data", "Data Engineering"),
            ("ai_ml", "AI/ML"),
            ("other", "Other"),
        ],
        validators=[Optional()],
    )

    skill_level = SelectField(
        "Skill Level",
        choices=[
            ("", "Select Skill Level"),
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
            ("expert", "Expert"),
        ],
        validators=[Optional()],
    )

    certifications = TextAreaField("Certifications")
    cloud_platforms = TextAreaField("Cloud Platforms")
    devops_tools = TextAreaField("DevOps Tools")
    version_control_systems = TextAreaField("Version Control Systems")
    programming_languages = TextAreaField("Programming Languages")
    monitoring_logging = TextAreaField("Monitoring & Logging")
    ci_cd_tools = TextAreaField("CI/CD Tools")
    other_technologies = TextAreaField("Other Technologies")
    expertise_areas = StringField("Expertise Areas", validators=[Optional(), Length(max=255)])
    technologies_led = TextAreaField("Technologies Led")
