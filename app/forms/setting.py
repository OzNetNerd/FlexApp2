from wtforms import StringField, TextAreaField, DateField, SelectField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Optional, Email, Length
from .base import BaseModelForm

class SettingForm(BaseModelForm):
    """Form for Setting"""
    # Add fields based on your Setting model
    # Example fields:
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    
    # Add other fields specific to Setting
