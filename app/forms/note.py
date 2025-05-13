from .base import BaseModelForm
from wtforms import TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired


class NoteForm(BaseModelForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    notable_type = SelectField(
        "Type",
        choices=[("User", "User"), ("Company", "Company"), ("Contact", "Contact"), ("Opportunity", "Opportunity")],
        validators=[DataRequired()],
    )
    notable_id = HiddenField("ID", validators=[DataRequired()])
    user_id = HiddenField("User ID")
