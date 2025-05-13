from .base import BaseModelForm
from wtforms import TextAreaField, HiddenField, DateTimeField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange

class SRSForm(BaseModelForm):
    question = TextAreaField('Question', validators=[DataRequired()])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    next_review_at = DateTimeField('Next Review', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    notable_type = SelectField('Type', choices=[
        ('Contact', 'Contact'),
        ('Company', 'Company'),
        ('Opportunity', 'Opportunity')
    ], validators=[DataRequired()])
    notable_id = HiddenField('ID', validators=[DataRequired()])
    interval = FloatField('Interval', validators=[Optional()], default=0)
    ease_factor = FloatField('Ease Factor', validators=[Optional()], default=2.5)

class ReviewHistoryForm(BaseModelForm):
    srs_item_id = SelectField('SRS Item', coerce=int, validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    interval = FloatField('Interval', validators=[DataRequired()])
    ease_factor = FloatField('Ease Factor', validators=[DataRequired()])