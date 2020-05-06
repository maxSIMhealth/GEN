from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='is_instructor')
def is_instructor(user, course):
    return bool(course in user.instructor.all())
