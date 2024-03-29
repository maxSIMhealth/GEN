from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from GEN.support_methods import duplicate_object, random_code_string


def requirement_fulfilled(user, item):
    """
    Check if all requirements have been fulfilled
    """
    from .models import Course, Status

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
                    requirement_status = requirement.status.filter(
                        learner=user, section=None
                    ).get()
                else:
                    requirement_status = requirement.status.filter(learner=user).get()
            except Status.DoesNotExist:
                requirement_status = None

            if requirement_status:
                fulfilled = requirement_status.completed
    else:
        fulfilled = True

    return fulfilled


def mark_section_completed(request, section):
    """
    Marks specified section status object as completed.

    Parameters
    ----------
    request
        object that contains metadata about the current user request
    section: Section
        section that will be marked as completed
    """

    from .models import Status

    section_status = Status.objects.get(learner=request.user, section=section)
    if not section_status.completed:
        section_status.completed = True
        section_status.save()
    else:
        messages.warning(request, _("This section is already marked as completed."))


def review_course_status(request, course, force: bool = False) -> bool:
    """
    Check all course sections' status objects and if they are all completed
    set the course status object as completed.
    If the `force` field is set as `True`, skips the check and set ALL sections
    and course statuses as completed.

    :param request: Django's HttpRequest object.
    :param course: Course object.
    :param force: Optional: Sets if the review should be skipped and forcefully set all status objects as completed.
    :return: Course completion status.
    """

    from courses.models import Status

    # course_type = course.type_name()
    # custom_completion_message = _(f"Congratulations, you have completed this {course_type}.")

    course_completed = False

    # get all course sections status objects
    status_objects = Status.objects.filter(learner=request.user, course=course)

    if force:
        # forcefully set all status objects (course and sections) as completed
        for status in status_objects:
            status.completed = True
            status.save()
            course_completed = True
            # messages.success(request, custom_completion_message)
    else:
        # if no section is set as incomplete, mark course status as completed
        if not status_objects.filter(completed=False).exclude(section=None):
            course_status = status_objects.get(section=None)
            course_status.completed = True
            course_status.save()
            course_completed = True
            # messages.success(request, custom_completion_message)

    return course_completed


def section_progress(item, items_participation, items_total, user):
    if item._meta.model_name == "section":
        # do not include section item (e.g., quiz) that is owned by the user in total count
        if hasattr(item, "author"):
            if not item.author == user:
                items_total += 1
        else:
            items_total += 1
        if item.status.filter(learner=user, completed=True).exists():
            items_participation += 1
    return items_participation, items_total


def quiz_section_progress(item, items_participation, items_total, user):
    if item._meta.model_name == "quiz":
        # do not include section item (e.g., quiz) that is owned by the user in total count
        if hasattr(item, "author"):
            if not item.author == user:
                items_total += 1
        else:
            items_total += 1
        if item.quizscore_set.filter(student=user).exists():
            items_participation += 1
    return items_participation, items_total


def discussion_section_progress(item, items_participation, items_total, user):
    if item._meta.model_name == "discussion":
        items_total += 1
        if item.comments.filter(author=user).exists():
            items_participation += 1
    return items_participation, items_total


def progress(user, course, items):
    from core.support_methods import allow_access

    items = items.filter(published=True)
    items_total = 0
    items_participation = 0

    for item in items:
        if item._meta.model_name != "section":
            access_allowed = allow_access(user, course, item)
        else:
            access_allowed = True

        if access_allowed:
            items_participation, items_total = discussion_section_progress(
                item, items_participation, items_total, user
            )

            items_participation, items_total = quiz_section_progress(
                item, items_participation, items_total, user
            )

            items_participation, items_total = section_progress(
                item, items_participation, items_total, user
            )

    items_progress = {"max": items_total, "current": items_participation}

    return items_progress


def duplicate_course(course, request, **kwargs):
    """
    Duplicates a whole course and all related objects EXCEPT user submissions and content.
    The new course will have no participants except the user that called the duplication.
     *WARNING*: ALL cross-references (e.g., requirements, videos inside a quiz) and outputs
    (e.g., upload creating a discussion board) will be reset and will have to be defined manually.

    :param request: Django's HttpRequest object.
    :param course: Course object that will be duplicated.
    :param kwargs: Optional: additional fields and values.
    :return: Course object.
    """

    original_course_pk = course.pk
    original_course_learners = course.learners.all()
    random_code = random_code_string(5)
    new_code = f"Copy_{random_code}"

    # clone course object
    new_course = duplicate_object(
        course, code=new_code, auto_enroll=False, requirement=None, **kwargs
    )

    # set current user as course member, instructor and editor
    new_course.members.add(request.user)
    new_course.instructors.add(request.user)
    new_course.editors.add(request.user)

    # clone sections objects and section items objects
    from courses.models import Section

    sections = Section.objects.filter(course=original_course_pk)

    for section in sections:
        duplicate_section(new_course, original_course_learners, section)

    messages.add_message(
        request,
        messages.WARNING,
        _(
            "WARNING: all cross-references, requirements and outputs have been reset for the new duplicate course and \
        all of its sections and items. You will need to set them manually.\
        User content is not duplicated and auto-enrollment was also disabled."
        ),
    )

    return new_course


def duplicate_section(new_course, original_course_learners, section):
    from courses.models import Section

    original_section_pk = section.pk

    # duplicate section
    new_section = section.duplicate(
        course=new_course,
        requirement=None,
        # output -> discussion board
        create_discussions=False,
        section_output=None,
        output_author_access_override=False,
        # output -> quiz
        clone_quiz=False,
        clone_quiz_reference=None,
        clone_quiz_output_section=None,
        clone_quiz_update_owner=False,
    )

    # duplicate items
    original_section = Section.objects.get(pk=original_section_pk)
    duplicate_section_items(
        new_course, new_section, original_course_learners, original_section
    )


def duplicate_section_items(new_course, new_section, original_course_learners, section):
    from content.models import ContentItem, ImageFile
    from discussions.models import Discussion
    from games.models import Game
    from quiz.models import Quiz
    from videos.models import VideoFile

    section_items_content = ContentItem.objects.filter(section=section)
    section_items_image = ImageFile.objects.filter(section=section)
    section_items_game = Game.objects.filter(section=section)
    section_items_video = VideoFile.objects.filter(section=section).exclude(
        author__in=original_course_learners
    )  # removing learners' content from queryset
    section_items_discussion = Discussion.objects.filter(section=section).exclude(
        author__in=original_course_learners
    )  # removing learners' content from queryset
    section_items_quiz = Quiz.objects.filter(section=section).exclude(
        author__in=original_course_learners
    )  # removing learners' content from queryset

    duplicate_section_item_content(new_section, section_items_content)
    duplicate_section_item_image(new_section, section_items_image)
    duplicate_section_item_video(new_course, new_section, section_items_video)
    duplicate_section_item_discussion(new_course, new_section, section_items_discussion)
    duplicate_section_item_quiz(new_course, new_section, section_items_quiz)
    duplicate_section_item_game(new_section, section_items_game)


def duplicate_section_item_game(new_section, section_items_game):
    if section_items_game is not None:
        for item in section_items_game:
            item.duplicate(section=new_section)


def duplicate_section_item_quiz(new_course, new_section, section_items_quiz):
    if section_items_quiz is not None:
        for item in section_items_quiz:
            item.duplicate(
                course=new_course, section=new_section, video=None, requirement=None
            )


def duplicate_section_item_discussion(
    new_course, new_section, section_items_discussion
):
    if section_items_discussion is not None:
        for item in section_items_discussion:
            item.duplicate(
                course=new_course,
                section=new_section,
                video=None,
                requirement=None,
            )


def duplicate_section_item_video(new_course, new_section, section_items_video):
    if section_items_video is not None:
        for item in section_items_video:
            item.duplicate(course=new_course, section=new_section)


def duplicate_section_item_image(new_section, section_items_image):
    if section_items_image is not None:
        for item in section_items_image:
            item.duplicate(section=new_section, file=True)


def duplicate_section_item_content(new_section, section_items_content):
    from content.models import ContentItem

    if section_items_content is not None:
        for item in section_items_content:
            # for some reason PdfFile was not duplicating correctly using the generic method
            # it was necessary to create a specific duplicate method for it
            is_pdf = False
            try:
                is_pdf = hasattr(item, "pdffile")
            except ContentItem.pdffile.RelatedObjectDoesNotExist:
                pass

            if is_pdf:
                from content.models import PdfFile

                pdf_item = PdfFile.objects.get(pk=item.pk)
                pdf_item.duplicate(section=new_section, file=True)
            else:
                item.duplicate(section=new_section)
