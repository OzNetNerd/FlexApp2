from .base import BaseModelForm
from wtforms import SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class CrispForm(BaseModelForm):
    relationship_id = SelectField("Relationship", coerce=int, validators=[DataRequired()])
    credibility = IntegerField("Credibility", validators=[DataRequired(), NumberRange(min=0, max=10)])
    reliability = IntegerField("Reliability", validators=[DataRequired(), NumberRange(min=0, max=10)])
    intimacy = IntegerField("Intimacy", validators=[DataRequired(), NumberRange(min=0, max=10)])
    self_orientation = IntegerField("Self-Orientation", validators=[DataRequired(), NumberRange(min=1, max=10)])
    notes = TextAreaField("Notes")
