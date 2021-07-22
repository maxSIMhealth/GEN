from courses.models import SectionItem


def allow_access(user, course, item):
    """
    Verifies if the user has permission to access an specific SectionItem.
    """

    access_restriction = item.access_restriction

    if access_restriction == SectionItem.PUBLIC and user in course.members.all():
        access_allowed = True
    elif access_restriction == SectionItem.INSTRUCTORS and user in course.instructors.all():
        access_allowed = True
    elif access_restriction == SectionItem.ADMINS and user.is_staff:
        access_allowed = True
    else:
        access_allowed = False

    return access_allowed