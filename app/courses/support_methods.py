from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Course, Status


def requirement_fulfilled(user, item):
    """
    Check if all requirements have been fulfilled
    """
    requirement = item.requirement
    is_course = isinstance(item, Course)
    course = item if is_course else item.course
    fulfilled = False

    # check if user is a course instructor or system staff
    is_instructor = bool(course in user.instructor.all())
    if is_instructor or user.is_staff:
        fulfilled = True
    else:
        # check if requirement has a related Status object for the user
        try:
            if is_course:
                requirement_status = requirement.status.filter(learner=user, section=None).get()
            else:
                requirement_status = requirement.status.filter(learner=user).get()
        except Status.DoesNotExist:
            requirement_status = None

        if requirement_status:
            fulfilled = requirement_status.completed

    return fulfilled


def section_mark_completed(request, section):
    """
    Marks specified section status object as completed.

    Parameters
    ----------
    request
        object that contains metadata about the current user request
    section: Section
        section that will be marked as completed
    """

    section_status = Status.objects.get(learner=request.user, section=section)
    if not section_status.completed:
        section_status.completed = True
        section_status.save()
    else:
        messages.warning(
            request,
            _("This section is already marked as completed.")
        )


def course_mark_completed(request, course):
    """
    Marks all status objects (course and sections) related to the user as completed.

    Parameters
    ----------
    request
        object that contains metadata about the current user request
    course: Course
        course that contains the status objects
    """

    statuses = Status.objects.filter(learner=request.user, course=course)
    for status in statuses:
        status.completed = True
        status.save()
