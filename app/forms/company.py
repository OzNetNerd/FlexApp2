from .base import BaseModelForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class CompanyForm(BaseModelForm):
    name = StringField("Company Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description")
