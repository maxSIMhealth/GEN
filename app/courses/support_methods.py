from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Course, Status


def requirement_fulfilled(user, item):
    """
    Check if all requirements have been fulfilled
    """
    requirement = item.requirement
    fulfilled = False

    if requirement:
        is_course = isinstance(item, Course)
        course = item if is_course else item.course


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
    else:
        fulfilled = True

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


def progress(user, course, items):
    from core.support_methods import allow_access

    items = items.filter(published = True)
    items_total = 0
    items_participation = 0

    for item in items:
        if item._meta.model_name != "section":
            access_allowed = allow_access(user, course, item)
        else:
            access_allowed = True

        if access_allowed == True:
            # do not include section item (e.g., quiz) that is owned by the user in total count
            if hasattr(item,'author'):
                if not item.author == user:
                    items_total += 1
            else:
                items_total += 1

            if item._meta.model_name == "discussion":
                if item.comments.filter(author=user).exists():
                    items_participation += 1
            if item._meta.model_name == "quiz":
                if item.quizscore_set.filter(student=user).exists():
                    items_participation += 1
            if item._meta.model_name == "section":
                if item.status.filter(learner=user, completed=True).exists():
                    items_participation += 1

    items_progress = {"max": items_total, "current": items_participation}

    return items_progress