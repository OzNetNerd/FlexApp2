from .base import BaseModelForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

class SettingForm(BaseModelForm):
    key = StringField('Key', validators=[DataRequired(), Length(max=100)])
    value = TextAreaField('Value')