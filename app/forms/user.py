from .base import BaseModelForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class UserForm(BaseModelForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField(
        "Password", validators=[Optional(), Length(min=8, message="Password must be at least 8 characters")]  # Optional for updates
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[Optional(), EqualTo("password", message="Passwords must match")]  # Optional for updates
    )
    is_admin = BooleanField("Admin Access")
