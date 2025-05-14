"""
SRS form classes for user input handling.

This module defines the forms used for SRS-related user input
in the web application, including validation rules.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, HiddenField, DateField
from wtforms.validators import DataRequired, Length, Optional


class SRSForm(FlaskForm):
    """Form for creating and editing SRS cards.

    This form handles the input for creating and editing SRS flash cards,
    including category selection, question/answer fields, and review options.
    """

    category = SelectField(
        'Category',
        validators=[DataRequired()],
        description='Select the category this card belongs to'
    )

    question = TextAreaField(
        'Question/Front',
        validators=[DataRequired(), Length(min=1, max=2000)],
        description='The question or prompt that will appear on the front of the card'
    )

    answer = TextAreaField(
        'Answer/Back',
        validators=[DataRequired(), Length(min=1, max=5000)],
        description='The answer that will appear on the back of the card'
    )

    tags = StringField(
        'Tags',
        validators=[Optional(), Length(max=200)],
        description='Comma-separated list of tags to help organize your cards'
    )

    review_immediately = BooleanField(
        'Available for review immediately',
        default=False,
        description='Make this card available for review right away'
    )

    action = HiddenField('Save Action', default='save')


class CategoryForm(FlaskForm):
    """Form for creating new card categories/decks.

    This form handles the input for creating new categories or decks
    for organizing flash cards.
    """

    name = StringField(
        'Category Name',
        validators=[DataRequired(), Length(min=1, max=50)],
        description='Name of the category or deck'
    )

    color = StringField(
        'Color',
        validators=[Optional(), Length(max=20)],
        description='Color code for the category (e.g., #ff0000 for red)'
    )


class ReviewForm(FlaskForm):
    """Form for submitting card reviews.

    This form handles the submission of review ratings for cards.
    """

    rating = HiddenField(
        'Rating',
        validators=[DataRequired()],
        description='Rating from 0-4 based on recall difficulty'
    )


class FilterForm(FlaskForm):
    """Form for filtering cards.

    This form handles filtering options for the card list views.
    """

    category = SelectField(
        'Category',
        validators=[Optional()],
        description='Filter by category'
    )

    due_only = BooleanField(
        'Due cards only',
        default=False,
        description='Show only cards due for review'
    )

    search = StringField(
        'Search',
        validators=[Optional(), Length(max=100)],
        description='Search in question or answer text'
    )

    sort_by = SelectField(
        'Sort by',
        choices=[
            ('next_review_at', 'Next review time'),
            ('created_at', 'Creation date'),
            ('last_reviewed_at', 'Last review date'),
            ('interval', 'Interval'),
            ('ease_factor', 'Difficulty'),
            ('review_count', 'Review count')
        ],
        default='next_review_at',
        description='Field to sort results by'
    )

    sort_order = SelectField(
        'Sort order',
        choices=[
            ('asc', 'Ascending'),
            ('desc', 'Descending')
        ],
        default='asc',
        description='Sort order (ascending or descending)'
    )

    min_interval = StringField(
        'Min Interval',
        validators=[Optional()],
        description='Minimum interval (days)'
    )

    max_interval = StringField(
        'Max Interval',
        validators=[Optional()],
        description='Maximum interval (days)'
    )

    min_ease = StringField(
        'Min Ease Factor',
        validators=[Optional()],
        description='Minimum ease factor'
    )

    max_ease = StringField(
        'Max Ease Factor',
        validators=[Optional()],
        description='Maximum ease factor'
    )


class BatchActionForm(FlaskForm):
    """Form for batch actions on selected cards.

    This form handles batch operations like review, reset, or delete
    on multiple selected cards.
    """

    batch_action = SelectField(
        'Action',
        choices=[
            ('review', 'Review Selected'),
            ('reset', 'Reset Progress'),
            ('delete', 'Delete Cards')
        ],
        validators=[DataRequired()],
        description='Action to perform on selected cards'
    )

    selected_cards = HiddenField(
        'Selected Cards',
        validators=[DataRequired()],
        description='Comma-separated list of selected card IDs'
    )


class ReviewHistoryForm(FlaskForm):
    """Form for viewing and filtering review history."""

    start_date = DateField(
        'Start Date',
        validators=[Optional()],
        format='%Y-%m-%d',
        description='Filter reviews starting from this date'
    )

    end_date = DateField(
        'End Date',
        validators=[Optional()],
        format='%Y-%m-%d',
        description='Filter reviews up to this date'
    )

    category = SelectField(
        'Category',
        validators=[Optional()],
        description='Filter by card category'
    )