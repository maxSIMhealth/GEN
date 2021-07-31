from django import template

from core.support_methods import course_sections_list
from courses.support_methods import requirement_fulfilled

register = template.Library()


@register.inclusion_tag("partials/section_navbar.html", takes_context=True)
def generate_sections_navbar(context):
    user = context["user"]
    course = context["course"]
    sections = course_sections_list(course, user)

    if "section" in context:
        current_section = context["section"]
    else:
        # TODO: improve this (this name is hard coded in views/course_info)
        current_section = context["section_name"]

    # generate list with section ids
    sections_list = list(sections.values_list('id', flat=True))
    # list(sections.values_list('id', flat=True)).index(context['section'].id)

    if current_section == 'Info':
        previous_section = None
        next_section_id = sections_list[0]
        next_section = sections.filter(pk=next_section_id)[0]
        current_section_position = None
        if next_section.requirement:
            next_section.requirement.fulfilled = requirement_fulfilled(user, next_section)
    else:
        # get position of current section
        current_section_position = sections_list.index(current_section.id)

        try:
            previous_section_id = sections_list[sections_list.index(current_section.id) - 1]
            if current_section_position == 0:
                previous_section = course
            else:
                previous_section = sections.filter(pk=previous_section_id)[0]
                if previous_section.requirement:
                    previous_section.requirement.fulfilled = requirement_fulfilled(user, previous_section)
        except IndexError:
            previous_section = None

        try:
            next_section_id = sections_list[sections_list.index(current_section.id) + 1]
            if current_section_position == sections_list[-1]:
                next_section = None
            else:
                next_section = sections.filter(pk=next_section_id)[0]
                if next_section.requirement:
                    next_section.requirement.fulfilled = requirement_fulfilled(user, next_section)
        except IndexError:
            next_section = None

    return {
        "current_section_position": current_section_position,
        "previous_section": previous_section,
        "next_section": next_section
    }
