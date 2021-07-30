from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import Q

from courses.models import PUBLIC, LEARNERS, INSTRUCTORS, EDITORS


# FIXME: this is a DEBUG ONLY function
@login_required
def reset(request):
    user = request.user
    is_instructor = bool(user.instructor.all())

    if not is_instructor:
        section_items = user.section_items.all()  # for video items
        quiz_scores = user.quizscore_set.all()
        quiz_attempts_answers = user.questionattempt_set.all()
        statuses = user.status.all()

        user_objects = [section_items, quiz_scores, quiz_attempts_answers, statuses]

        for element in user_objects:
            for item in element:
                item.delete()

    return redirect("home")


def check_is_instructor(course_object, user):
    is_instructor = bool(course_object in user.instructor.all())

    return is_instructor


def check_is_editor(course_object, user):
    is_editor = bool(course_object in user.editor.all())

    return is_editor


def course_sections_list(course_object, user):
    # check if user is a course instructor or editor
    is_instructor = check_is_instructor(course_object, user)
    is_editor = check_is_editor(course_object, user)

    # show all sections if the user is a course instructor, superuser, or staff
    if user.is_superuser or user.is_staff:
        sections = course_object.sections.all()
    elif is_editor:
        sections = course_object.sections.filter(Q(access_restriction=PUBLIC) | Q(access_restriction=EDITORS))
    elif is_instructor:
        sections = course_object.sections.filter(Q(access_restriction=PUBLIC) | Q(access_restriction=INSTRUCTORS))
    else:
        sections = course_object.sections.filter((Q(access_restriction=PUBLIC) | Q(access_restriction=LEARNERS)) & Q(published=True))

    return sections
