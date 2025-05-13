from .base import BaseModelForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, HiddenField
from wtforms.validators import DataRequired, Optional, Length


class TaskForm(BaseModelForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description")
    due_date = DateTimeField("Due Date", validators=[Optional()], format="%Y-%m-%d %H:%M:%S")
    status = SelectField(
        "Status",
        choices=[
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("On Hold", "On Hold"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled"),
        ],
        default="Pending",
    )
    priority = SelectField(
        "Priority", choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Urgent", "Urgent")], default="Medium"
    )
    assigned_to_id = SelectField("Assigned To", coerce=int, validators=[Optional()])
    notable_type = SelectField(
        "Type",
        choices=[("User", "User"), ("Company", "Company"), ("Contact", "Contact"), ("Opportunity", "Opportunity")],
        validators=[DataRequired()],
    )
    notable_id = HiddenField("ID", validators=[DataRequired()])
