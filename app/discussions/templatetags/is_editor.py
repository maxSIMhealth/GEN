from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter(name="is_editor")
def is_editor(user, course):
    """
    Checks if user is set as a course editor.

    :param user: integer or User object.
    :param course: course object.
    :return: boolean value.
    """
    if type(user) is int:
        user = User.objects.get(pk=user)

    return bool(course in user.editor.all())
