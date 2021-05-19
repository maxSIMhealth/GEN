from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


# FIXME: this is a DEBUG ONLY function
@login_required
def reset(request):
    user = request.user
    is_instructor = bool(user.instructor.all())

    if not is_instructor:
        section_items = user.section_items.all()  # for video items
        quiz_scores = user.quizscore_set.all()
        quiz_attempts_answers = user.questionattempt_set.all()

        user_objects = [section_items, quiz_scores, quiz_attempts_answers]

        for element in user_objects:
            for item in element:
                item.delete()

    return redirect("home")


def check_is_instructor(course_object, user):
    is_instructor = bool(course_object in user.instructor.all())

    return is_instructor


def course_sections_list(course_object, user):
    # check if user is a course instructor
    is_instructor = check_is_instructor(course_object, user)

    # show all sections if the user is a course instructor, superuser, or staff
    if is_instructor or user.is_superuser or user.is_staff:
        sections = course_object.sections.all()
    else:
        sections = course_object.sections.filter(published=True)

    return sections
