from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from GEN.decorators import course_enrollment_check
from GEN.support_methods import enrollment_test

from core.views import check_is_instructor
from courses.support_methods import requirement_fulfilled
from .models import Course, Section, SectionItem, Status
from .progress import progress


not_enrolled_error = _("You are not enrolled in the requested course.")


@login_required
@course_enrollment_check(enrollment_test)
def course(request, pk):
    user = request.user
    course_object = get_object_or_404(Course, pk=pk)
    discussions = course_object.discussions.all()
    quizzes = course_object.quizzes.all()
    # user = request.user
    # TODO: improve this: I've hard-corded this section name because info isn't a dynamic section item
    section_name = "Info"

    # check_user_enrollment(request, user, course_object)

    # progress status
    discussions_progress = progress(request, discussions)
    quizzes_progress = progress(request, quizzes)

    return render(
        request,
        "sections/section_info.html",
        {
            "course": course_object,
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
    allow_submission_list = []
    allow_submission = False
    start_date_reached = False
    end_date_passed = False
    section_status, section_status_created = Status.objects.get_or_create(
        learner=request.user,
        course=course_object,
        section=section_object
    )

    if request.method == "POST":
        # TODO: check section type and set completed status based on its contents

        if not section_status.completed:
            section_status.completed = True
            section_status.save()
        else:
            messages.warning(
                request,
                _("This section is already marked as completed.")
            )

        my_kwargs = dict(
            pk=course_object.pk,
            section_pk=section_object.pk
        )

        return redirect("section", **my_kwargs)


    # check_user_enrollment(request, user, course_object)

    is_instructor = check_is_instructor(course_object, user)

    # check if section has start and end dates

    # check if section start date
    if section_object.start_date:
        if timezone.now() < section_object.start_date:
            if not is_instructor:
                messages.warning(
                    request,
                    _(
                        "This section's contents are not yet available because the start date has not been reached."
                    ),
                )
                # clear out section items
                section_items = SectionItem.objects.none()
            else:
                messages.info(
                    request,
                    _(
                        "This section and its contents are not yet available to learners because of the start date."
                    ),
                )
        else:
            start_date_reached = True

    # check section end date
    # FIXME: instead of totally hiding the content, maybe I could just disable the links
    if section_object.end_date:
        if timezone.now() > section_object.end_date:
            end_date_passed = True

            if not is_instructor:
                messages.warning(
                    request,
                    _(
                        "This section is closed and its contents have been hidden or disabled because the end date has passed."
                    ),
                )
                # clear out section items
                section_items = SectionItem.objects.none()
            else:
                messages.info(
                    request,
                    _(
                        "This section is closed and its contents have been hidden or disabled to learners because the end date has passed."
                    ),
                )

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
        section_template = "sections/section_quiz.html"
    elif section_object.section_type == "D":
        section_template = "sections/section_discussion.html"
    elif section_object.section_type == "V":
        if is_instructor:
            # getting all section items (even not published)
            section_items = section_object.section_items
        section_template = "sections/section_videos.html"
    elif section_object.section_type == "U":
        section_template = "sections/section_upload.html"
        # getting all section items (even not published) and filtering by user
        section_items = section_object.section_items.filter(author=request.user)

        # checking section start and end dates to decide if submission should be enabled
        if section_object.start_date:
            if start_date_reached:
                allow_submission_list.append(True)
            else:
                allow_submission_list.append(False)

        if section_object.end_date:
            if end_date_passed:
                allow_submission_list.append(False)
            elif not end_date_passed:
                allow_submission_list.append(True)

        # if there is no section item, allow submission
        if not section_items:
            allow_submission_list.append(True)
        else:
            allow_submission_list.append(False)

        allow_submission = all(element for element in allow_submission_list)

    elif section_object.section_type == "C":
        section_template = "sections/section_content.html"

    return render(
        request,
        section_template,
        {
            "course": course_object,
            "section": section_object,
            "section_items": section_items,
            "section_status": section_status,
            "gamification": gamification,
            "allow_submission": allow_submission,
        },
    )