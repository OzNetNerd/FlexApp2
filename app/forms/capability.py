from wtforms import StringField, TextAreaField, DateField, SelectField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Optional, Email, Length
from .base import BaseModelForm


class CapabilityForm(BaseModelForm):
    """Form for Capability"""

    # Add fields based on your Capability model
    # Example fields:
    name = StringField("Name", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[Optional()])

    # Add other fields specific to Capability
