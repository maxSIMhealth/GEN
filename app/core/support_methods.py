from courses.models import PUBLIC, LEARNERS, INSTRUCTORS, EDITORS, ADMINS


def allow_access(user, course, item):
    """
    Verifies if the user has permission to access an specific SectionItem.
    """

    access_restriction = item.access_restriction

    if access_restriction == PUBLIC and user in course.members.all():
        access_allowed = True
    elif access_restriction == LEARNERS and user in course.learners.all():
        access_allowed = True
    elif access_restriction == INSTRUCTORS and user in course.instructors.all():
        access_allowed = True
    elif access_restriction == EDITORS and user in course.editors.all():
        access_allowed = True
    elif access_restriction == ADMINS and user.is_staff:
        access_allowed = True
    else:
        access_allowed = False

    return access_allowed