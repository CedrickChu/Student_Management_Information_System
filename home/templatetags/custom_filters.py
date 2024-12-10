# yourapp/templatetags/custom_filters.py
from django import template
from home.models import StudentGrade

register = template.Library()

@register.filter
def get_grade(student_grades, subject_id, grading_period):
    """
    Returns the grade for a specific subject and grading period.
    """
    try:
        grade = student_grades.filter(subject__id=subject_id).first()
        if grade:
            return getattr(grade, grading_period, None)
        return None
    except StudentGrade.DoesNotExist:
        return None
