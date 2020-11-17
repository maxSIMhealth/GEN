from django import template

from courses.support_methods import requirement_fulfilled
from core.views import course_sections_list

register = template.Library()


@register.inclusion_tag("section_tabs.html", takes_context=True)
def show_sections(context, sections):
    user = context["user"]
    course = context["course"]
    sections = course_sections_list(course, user)
    # sections = sections.all()
    if "section" in context:
        current_section = context["section"]
    else:
        # TODO: improve this (this name is hard coded in views/course_info)
        current_section = context["section_name"]

    for section in sections:
        if section.requirement:
            section.requirement.fulfilled = requirement_fulfilled(user, section)

    return {"sections": sections, "current_section": current_section}
