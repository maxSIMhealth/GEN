from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter(name="is_instructor")
def is_instructor(user, course):
    """
    Checks if user is set as a course instructor.

    :param user: integer or User object.
    :param course: course object.
    :return: boolean value.
    """
    if type(user) is int:
        user = User.objects.get(pk=user)

    return bool(course in user.instructor.all())
