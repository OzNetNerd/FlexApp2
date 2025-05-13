from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Optional, Email

class BaseModelForm(FlaskForm):
    """Base form class with common functionality"""
    
    @classmethod
    def from_model(cls, model):
        """Create form instance from model"""
        return cls(obj=model)
