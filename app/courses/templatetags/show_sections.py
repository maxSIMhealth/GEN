from django import template

from core.views import course_sections_list
from courses.support_methods import requirement_fulfilled

register = template.Library()


@register.inclusion_tag("sections/section_tabs.html", takes_context=True)
def show_sections(context):
    user = context["user"]
    course = context["course"]
    sections = course_sections_list(course, user)

    if "section" in context:
        current_section = context["section"]
    else:
        # TODO: improve this (this name is hard coded in views/course_info)
        current_section = context["section_name"]

    for section in sections:
        if section.requirement:
            section.requirement.fulfilled = requirement_fulfilled(user, section)

    return {"sections": sections, "current_section": current_section}
