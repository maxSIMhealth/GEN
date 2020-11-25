from django import template

register = template.Library()


@register.filter(name="is_instructor")
def is_instructor(user, course):
    return bool(course in user.instructor.all())
