from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, IntegerField, FloatField, BooleanField, \
    HiddenField
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange, ValidationError


class BaseModelForm(FlaskForm):
    """Base form class with common functionality"""

    @classmethod
    def from_model(cls, model):
        """Create form instance from model"""
        return cls(obj=model)