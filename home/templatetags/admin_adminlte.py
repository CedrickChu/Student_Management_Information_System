import re
from django import template
from django.utils.html import format_html
from home.utils import get_menu_items
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import (PAGE_VAR)
from home.models import StudentGrade

register = template.Library()
assignment_tag = register.assignment_tag if hasattr(register, 'assignment_tag') else register.simple_tag


@register.filter
def clean_text(value):
    res = value.replace('\n', ' ')
    return res


@register.filter
def checkbox(value):
    res = re.sub(r"</?(?i:td)(.|\n)*?>", "", value)
    return res

@register.filter
def get_item(dictionary, key):
    """Retrieve a value from a dictionary using the key."""
    return dictionary.get(key)

@register.filter
def get_grade(student_grades, grading_period):
    """
    Returns the grade for a specific grading period of a student.
    If no grade is found, it returns 'Unposted'.
    """
    if not student_grades:
        return 'Unposted'

    # Get the grade for the specific grading period dynamically
    grade = student_grades.first()  # Assuming 'student_grades' is a queryset with one grade entry for a student
    if grade:
        return getattr(grade, grading_period, 'Unposted')  # Access the grade dynamically
    return 'Unposted'


@assignment_tag(takes_context=True)
def admin_get_menu(context):
    return get_menu_items(context)


@assignment_tag(takes_context=True)
def get_direction(context):
    res = {
        'panel': 'text-left',
        'notify': 'right',
        'float': 'float-right',
        'reverse_panel': 'text-right',
        'nav': 'ml-auto'
    }

    if context.get('LANGUAGE_BIDI'):
        res['panel'] = 'text-right'
        res['notify'] = 'left'
        res['float'] = ''
        res['reverse_panel'] = 'text-left'
        res['nav'] = 'mr-auto'
    return res


@assignment_tag(takes_context=True)
def get_admin_setting(context):
    # user = context.get('request').user
    # admin_black_setting = user.admin_black_setting if hasattr(user, 'admin_black_setting') else None
    res = {
        # 'sidebar_background': admin_black_setting.sidebar_background if admin_black_setting else 'primary',
        # 'dark_mode': admin_black_setting.dark_mode if admin_black_setting else True,
        # 'input_bg_color': '#ffffff' if admin_black_setting and not admin_black_setting.dark_mode else '#27293c'
    }

    return res


@register.simple_tag
def paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == cl.paginator.ELLIPSIS:
        return format_html('{} ', cl.paginator.ELLIPSIS)
    elif i == cl.page_num:
        return format_html('<a href="" class="page-link">{}</a> ', i)
    else:
        return format_html(
            '<a href="{}" class="page-link {}">{}</a> ',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe('end' if i == cl.paginator.num_pages else ''),
            i,
        )


@register.filter
def sum_number(value, number):
    return value + number


@register.filter
def neg_num(value, number):
    return value - number
