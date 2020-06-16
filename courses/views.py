from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from GEN.decorators import course_enrollment_check
from GEN.support_methods import enrollment_test

from courses.support_methods import requirement_fulfilled
from .models import Course, Section
from .progress import progress


not_enrolled_error = _("You are not enrolled in the requested course.")


@login_required
@course_enrollment_check(enrollment_test)
def course(request, pk):
    course_object = get_object_or_404(Course, pk=pk)
    sections = course_object.sections.filter(published=True)
    discussions = course_object.discussions.all()
    quizzes = course_object.quizzes.all()
    # user = request.user
    # TODO: improve this: I've hard-corded this section name because
    # info isn't a dynamic section item
    section_name = "Info"

    # check_user_enrollment(request, user, course_object)

    # progress status
    discussions_progress = progress(request, discussions)
    quizzes_progress = progress(request, quizzes)

    return render(
        request,
        "course.html",
        {
            "course": course_object,
            "sections": sections,
            "section_name": section_name,
            "discussions_progress": discussions_progress,
            "quizzes_progress": quizzes_progress,
        },
    )


@login_required
@course_enrollment_check(enrollment_test)
def section_page(request, pk, section_pk):
    course_object = get_object_or_404(Course, pk=pk)
    section_object = get_object_or_404(Section, pk=section_pk)
    section_items = section_object.section_items.filter(published=True)
    gamification = course_object.enable_gamification
    user = request.user
    requirement = section_object.requirement
    allow_submission = False

    # check_user_enrollment(request, user, course_object)

    # check if user is a course instructor
    is_instructor = bool(course_object in request.user.instructor.all())

    # only allow participant to access section if requirements have been fulfilled
    if requirement and not is_instructor:
        fulfilled = requirement_fulfilled(user, section_object)

        if not fulfilled:
            messages.error(
                request,
                _(
                    "You have not fulfilled the requirements to access the requested section."
                ),
            )
            return redirect("course", pk=course_object.pk)

    if section_object.section_type == "Q":
        section_template = "section_quiz.html"
    elif section_object.section_type == "D":
        section_template = "section_discussion.html"
    elif section_object.section_type == "V":
        if is_instructor:
            # getting all section items (even not published)
            section_items = section_object.section_items
        section_template = "section_videos.html"
    elif section_object.section_type == "U":
        section_template = "section_upload.html"
        # getting all section items (even not published) and filtering by user
        section_items = section_object.section_items.filter(author=request.user)
        # if there is no section item, allow submission
        if not section_items:
            allow_submission = True

    return render(
        request,
        section_template,
        {
            "course": course_object,
            "section": section_object,
            "section_items": section_items,
            "gamification": gamification,
            "allow_submission": allow_submission,
        },
    )
