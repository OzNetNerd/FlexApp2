from .base import BaseModelForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class UserForm(BaseModelForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[
        Optional(),  # Optional for updates
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(),  # Optional for updates
        EqualTo('password', message='Passwords must match')
    ])
    is_admin = BooleanField('Admin Access')