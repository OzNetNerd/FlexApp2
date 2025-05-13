from .base import BaseModelForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class OpportunityForm(BaseModelForm):
    name = StringField("Opportunity Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description")
    status = SelectField(
        "Status", choices=[("active", "Active"), ("won", "Won"), ("lost", "Lost"), ("suspended", "Suspended")], default="active"
    )
    stage = SelectField(
        "Stage",
        choices=[
            ("qualification", "Qualification"),
            ("needs_analysis", "Needs Analysis"),
            ("proposal", "Proposal"),
            ("negotiation", "Negotiation"),
            ("closed", "Closed"),
        ],
        default="qualification",
    )
    value = FloatField("Value", validators=[Optional(), NumberRange(min=0)])
    priority = SelectField("Priority", choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium")
    close_date = DateTimeField("Close Date", validators=[Optional()], format="%Y-%m-%d")
    company_id = SelectField("Company", coerce=int, validators=[Optional()])
