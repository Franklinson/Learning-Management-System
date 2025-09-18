"""Custom validators for the LMS application."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_lesson_order(value):
    """Validate that lesson order is positive."""
    if value <= 0:
        raise ValidationError(
            _('Lesson order must be a positive integer.'),
            code='invalid_order'
        )


def validate_quiz_score(value):
    """Validate that quiz score is non-negative."""
    if value < 0:
        raise ValidationError(
            _('Quiz score cannot be negative.'),
            code='invalid_score'
        )


def validate_course_title(value):
    """Validate course title format."""
    if len(value.strip()) < 3:
        raise ValidationError(
            _('Course title must be at least 3 characters long.'),
            code='title_too_short'
        )
    
    if value.strip() != value:
        raise ValidationError(
            _('Course title cannot start or end with whitespace.'),
            code='invalid_whitespace'
        )