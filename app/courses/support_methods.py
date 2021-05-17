from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from discussions.support_methods import has_participated
from quiz.support_methods import quiz_score_get

from .models import Status

def requirement_fulfilled(user, section):
    """
    Check if all section requirements have been fulfilled
    """
    requirement = section.requirement

    fulfilled = False
    items_completed = []
    # check if user is a course instructor or system staff
    is_instructor = bool(section.course in user.instructor.all())
    if is_instructor or user.is_staff:
        fulfilled = True
    else:
        # check if requirement has a related Status object for the user
        try:
            requirement_status = requirement.status.filter(learner=user).get()
        except Status.DoesNotExist:
            requirement_status = None

        if requirement_status:
            fulfilled = requirement_status.completed

        # for item in requirement.section_items.all():
        #     if requirement.section_type == "Q":
        #         items_completed.append(quiz_score_get(user, item.quiz).exists())
        #     elif requirement.section_type == "D":
        #         items_completed.append(has_participated(user, item.discussion))
        #     elif requirement.section_type == "U":
        #         item_uploaded = (
        #             requirement.section_items.all()
        #             .filter(author=user, published=True)
        #             .count()
        #             > 0
        #         )
        #         items_completed.append(item_uploaded)
        #     elif requirement.section_type == "V":
        #         if item.videofile.quizzes.exists():
        #             for quiz in item.videofile.quizzes.all():
        #                 items_completed.append(quiz_score_get(user, quiz).exists())
        #     else:
        #         items_completed.append(False)
        #
        #     fulfilled = all(element for element in items_completed)

    return fulfilled


def section_mark_completed(request, section):
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
    sections_statuses = Status.objects.filter(learner=request.user, course=course)
    for status in sections_statuses:
        status.completed = True
        status.save()