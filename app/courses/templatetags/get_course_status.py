from courses.support_methods import progress

from django import template

register = template.Library()


@register.simple_tag
def get_course_status(user, course):
    sections = course.sections.filter(published=True)
    sections_progress = progress(user, course, sections)

    # course status codes
    # 0 = not started
    # 1 = started
    # 2 = completed

    if sections_progress["current"] == sections_progress["max"]:
        course_status = 2
    elif sections_progress["max"] > sections_progress["current"] > 0:
        course_status = 1
    else:
        course_status = 0

    return course_status
