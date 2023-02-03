import io
import textwrap

from core.support_methods import check_is_instructor, filter_by_access_restriction
from courses.support_methods import (
    mark_section_completed,
    progress,
    review_course_status,
)
from games.models import MoveToColumnsGroup
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

import GEN.settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from GEN.decorators import check_permission, check_requirement, course_enrollment_check
from GEN.support_methods import enrollment_test

from .models import CERTIFICATE_COURSE, Course, Section, SectionItem, Status

not_enrolled_error = _("You are not enrolled in the requested course.")
certificate_title = _("Certificate of Completion")
certificate_presented_to = _("This certificate is presented to")
certificate_for_completing = _("for completing the")
certificate_generated_on = _("Generated on")


@login_required
@course_enrollment_check(enrollment_test)
@check_requirement()
def course(request, pk):
    user = request.user
    course_object = get_object_or_404(Course, pk=pk)
    sections = course_object.sections.filter(published=True)
    sections = filter_by_access_restriction(course_object, sections, user)
    discussions = course_object.discussions.all()
    discussions = filter_by_access_restriction(course_object, discussions, user)
    quizzes = course_object.quizzes.all()
    quizzes = filter_by_access_restriction(course_object, quizzes, user)
    course_type = course_object.type_name()
    section_name = course_object.initial_section_name

    # create status object for course and sections, if they don't exist
    # TODO: this should only be done on first access
    for section in sections:
        if section.published:
            Status.objects.get_or_create(
                learner=user, course=course_object, section=section
            )
    course_object.status.get_or_create(learner=user, course=course_object, section=None)

    # progress status
    discussions_progress = progress(request.user, course_object, discussions)
    quizzes_progress = progress(request.user, course_object, quizzes)
    sections_progress = progress(request.user, course_object, sections)

    # TODO: this should be unnecessary, review and remove
    course_completed = (
        True if sections_progress["current"] == sections_progress["max"] else False
    )
    course_status = course_object.status.get(learner=user, section=None)
    if course_completed and course_status.completed is False:
        course_status.completed = True
        course_status.save()

    # messages
    msg_course_completed = _(f"Congratulations! You have completed this {course_type}.")
    msg_certificate_available = _(
        "\nYour certificate of completion is now available in the 'Course Details' area below."
    )
    msg_go_to_next_course = _(
        f"\nPlease go to the Home page to access the next {course_type}."
    )

    # FIXME: implement proper course grouping
    last_course_object = user.member.last()
    if course_object == last_course_object:
        last_course = True
    else:
        last_course = False

    if course_completed:
        message_congratulations = msg_course_completed
        if course_object.provide_certificate:
            message_congratulations += msg_certificate_available
        if not last_course:
            message_congratulations += msg_go_to_next_course
    else:
        message_congratulations = None

    return render(
        request,
        "sections/section_info.html",
        {
            "course": course_object,
            "course_completed": course_completed,
            "section_name": section_name,
            "discussions_progress": discussions_progress,
            "quizzes_progress": quizzes_progress,
            "sections_progress": sections_progress,
            "message_congratulations": message_congratulations,
        },
    )


def render_section_content(section_items, section_object):
    from courses.models import SectionItem

    section_template = "sections/section_content.html"
    section_items = SectionItem.objects.filter(section=section_object, published=True)
    for item in section_items:
        # FIXME: it shouldn't be necessary to manually set item.type, the template should use item.item_type directly
        if item.item_type == SectionItem.SECTION_ITEM_VIDEO:
            item.type = "Video"
        elif item.item_type == SectionItem.SECTION_ITEM_CONTENT:
            item.type = "Content"
        elif item.item_type == SectionItem.SECTION_ITEM_GAME:
            item.type = "Game"
            if item.game.type == "MC":
                # get 'move to column' game elements
                game_elements = MoveToColumnsGroup.objects.filter(game=item)[0]
                item.game.info_json = serialize("json", [game_elements])
                item.game.source_items_json = serialize(
                    "json", game_elements.source_items.all()
                )
                item.game.choice1_items_json = serialize(
                    "json", game_elements.choice1_items.all()
                )
                item.game.choice2_items_json = serialize(
                    "json", game_elements.choice2_items.all()
                )
            elif item.game.type == "TB":
                # 'text boxes' game
                item.game.info_json = serialize("json", [item.game])
                item.game.terms = serialize("json", item.game.textboxesterm_set.all())
                item.game.items = serialize("json", item.game.textboxesitem_set.all())
            elif item.game.type == "MT":
                # 'match terms' game
                item.game.terms = serialize("json", item.game.textboxesterm_set.all())
                item.game.items = serialize("json", item.game.textboxesitem_set.all())
        elif item.item_type == SectionItem.SECTION_ITEM_ZIP:
            item.type = "Zip"
        else:
            item.type = None
    return section_items, section_template


def render_section_upload(
    allow_submission,
    allow_submission_list,
    end_date_passed,
    request,
    section_items,
    section_object,
    start_date_reached,
):
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
    return allow_submission, section_items, section_template


def render_section_video(is_instructor, section_items, section_object):
    if is_instructor:
        # getting all section items (even not published)
        section_items = section_object.section_items
    section_template = "sections/section_videos.html"
    return section_items, section_template


def render_section_discussion(section_object, section_items):
    # sorting discussions based on parameter defined in the section
    # by default sectionitems are manually sorted (custom)
    section_items_ordering = section_object.items_ordering
    if section_items_ordering == section_object.ITEMS_ORDERING_CREATION_DATE:
        section_items = section_items.order_by("-created")
    section_template = "sections/section_discussion.html"
    return section_items, section_template


def render_section_quiz(section_items, section_object):
    if section_object.group_by_video:
        section_items = section_items
        section_template = "sections/section_quiz_grouped.html"
    else:
        section_template = "sections/section_quiz.html"
    return section_items, section_template


def render_section_scorm(is_instructor, section_items, section_object):
    if is_instructor:
        # getting all section items (even not published)
        section_items = section_object.section_items
    section_template = "sections/section_scorm.html"

    return section_items, section_template


def render_section_based_on_type(
    allow_submission,
    allow_submission_list,
    end_date_passed,
    is_instructor,
    request,
    section_items,
    section_object,
    start_date_reached,
):
    section_template = None

    if section_object.section_type == Section.SECTION_TYPE_QUIZ:
        section_items, section_template = render_section_quiz(
            section_items, section_object
        )
    elif section_object.section_type == Section.SECTION_TYPE_DISCUSSION:
        section_items, section_template = render_section_discussion(
            section_object, section_items
        )
    elif section_object.section_type == Section.SECTION_TYPE_VIDEO:
        section_items, section_template = render_section_video(
            is_instructor, section_items, section_object
        )
    elif section_object.section_type == Section.SECTION_TYPE_UPLOAD:
        allow_submission, section_items, section_template = render_section_upload(
            allow_submission,
            allow_submission_list,
            end_date_passed,
            request,
            section_items,
            section_object,
            start_date_reached,
        )

    elif section_object.section_type == Section.SECTION_TYPE_CONTENT:
        section_items, section_template = render_section_content(
            section_items, section_object
        )

    elif section_object.section_type == Section.SECTION_TYPE_SCORM:
        section_items, section_template = render_section_scorm(
            is_instructor, section_items, section_object
        )

    if not section_template:
        raise Exception(
            f"Section '{section_object}' of type '{section_object.section_type}' has no template defined."
        )

    return allow_submission, section_items, section_template


def check_section_dates(
    end_date_passed,
    is_instructor,
    request,
    section_items,
    section_object,
    start_date_reached,
):
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
    return end_date_passed, section_items, start_date_reached


def check_completion_status_and_display_messages(
    course_object, course_type, last_section, request, section_object, section_status
):
    # check course completion status
    course_completed = course_object.status.get(
        learner=request.user, section=None
    ).completed
    # messages
    msg_course_completed = _(f"Congratulations! You have completed this {course_type}.")
    msg_certificate_available = _(
        f"\nYour certificate of completion is now available in the "
        f"{course_object.initial_section_name} section."
    )
    msg_section_completed = _("Congratulations! You have completed this section.")
    msg_final_assessment_completed = _(
        "Congratulations! You have passed the assessment."
    )
    msg_go_to_next_section = _("\nPlease navigate to the next section.")
    # sets congratulations message, if the course or section is completed
    if course_completed:
        message_congratulations = msg_course_completed
        if course_object.provide_certificate:
            message_congratulations += msg_certificate_available
    elif section_status.completed:
        message_congratulations = msg_section_completed
        if section_object.final_assessment:
            message_congratulations = msg_final_assessment_completed
        if not last_section:
            message_congratulations += msg_go_to_next_section
        else:
            if course_object.provide_certificate:
                message_congratulations += msg_certificate_available
    else:
        message_congratulations = None
    return message_congratulations


@login_required
@course_enrollment_check(enrollment_test)
@check_permission("section")
@check_requirement()
def section_page(request, pk, section_pk):
    debug = GEN.settings.DEBUG
    user = request.user
    course_object = get_object_or_404(Course, pk=pk)
    course_type = course_object.type_name()
    section_object = get_object_or_404(Section, pk=section_pk)
    section_items = section_object.section_items.filter(published=True)
    section_items = filter_by_access_restriction(course_object, section_items, user)
    gamification = course_object.enable_gamification
    allow_submission_list = []
    allow_submission = False
    start_date_reached = False
    end_date_passed = False
    section_status, section_status_created = Status.objects.get_or_create(
        learner=request.user, course=course_object, section=section_object
    )

    # check if the current section is the last one
    last_section_object = course_object.sections.last()
    if section_object == last_section_object:
        last_section = True
    else:
        last_section = False

    message_congratulations = check_completion_status_and_display_messages(
        course_object,
        course_type,
        last_section,
        request,
        section_object,
        section_status,
    )

    if request.method == "POST":
        # TODO: check section type and set completed status based on its contents

        # set section status as completed
        mark_section_completed(request, section_object)

        # review course sections status, and set course as completed if all of them are completed
        review_course_status(request, course_object)

        my_kwargs = dict(pk=course_object.pk, section_pk=section_object.pk)

        return redirect("section", **my_kwargs)

    is_instructor = check_is_instructor(course_object, user)

    # check if section has start and end dates
    end_date_passed, section_items, start_date_reached = check_section_dates(
        end_date_passed,
        is_instructor,
        request,
        section_items,
        section_object,
        start_date_reached,
    )

    # set submission permission, items and template based on section type
    allow_submission, section_items, section_template = render_section_based_on_type(
        allow_submission,
        allow_submission_list,
        end_date_passed,
        is_instructor,
        request,
        section_items,
        section_object,
        start_date_reached,
    )

    return render(
        request,
        section_template,
        {
            "course": course_object,
            "section": section_object,
            "section_items": section_items,
            "section_status": section_status,
            "last_section": last_section,
            "gamification": gamification,
            "allow_submission": allow_submission,
            "message_congratulations": message_congratulations,
            "debug": debug,
        },
    )


@login_required
@course_enrollment_check(enrollment_test)
def generate_certificate(request, pk):
    """
    Generates certificate of conclusion as a PDF file.
    If CertificateLogoFiles exists, they will be used on the header portion.
    """
    course_object = get_object_or_404(Course, pk=pk)

    if course_object.provide_certificate:
        user = request.user
        sections_statuses = Status.objects.filter(learner=user, course=course_object)
        filename = f"GEN - {course_object.code} - {request.user.first_name} {request.user.last_name}.pdf"
        certificate_template = course_object.certificate_template
        date = timezone.localtime().isoformat()

        sections_completed = []
        for item in sections_statuses:
            sections_completed.append(item.completed)

        if all(sections_completed):
            return render_certificate_pdf(
                course_object, date, filename, certificate_template, request, user
            )
        else:
            messages.warning(
                request, _("You have not completed this course/module yet.")
            )
            return redirect("course", pk=course_object.pk)
    else:
        messages.warning(
            request,
            _("This course/module does not provide a certificate of conclusion."),
        )
        return redirect("course", pk=course_object.pk)


def render_certificate_pdf(course_object, date, filename, template, request, user):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    certificate = canvas.Canvas(buffer, pagesize=landscape(letter))
    certificate.setTitle(str(certificate_title))

    # Define 'term' for the course/module name
    if course_object.certificate_type == CERTIFICATE_COURSE:
        # actual course/module name
        certificate_term = course_object.name
    else:
        # custom name
        certificate_term = course_object.certificate_custom_term

    # Define if the course is referred to as course or as module
    course_type_name = course_object.type_name()

    # Template to be used
    if template is None:
        logos = None
        frame = None
    else:
        frame = template.frame
        logos = template.logos.all()
        if logos.count() == 0:
            logos = None

    # Page
    page_width = landscape(letter)[0]
    page_height = landscape(letter)[1]

    # Frame
    if frame is not None:
        frame_absolute_url = request.build_absolute_uri(frame.file.url)
        certificate.drawImage(
            frame_absolute_url, 0, 0, width=page_width, height=page_height
        )

    # Logos
    # The preferred logo size 200 x 80 points.
    # Width is fixed at 200 and height is automatically calculated while maintaining proportion.
    logo_spacing = 20
    logo_width = 200
    logo_max_height = 80
    logos_reserved_space = logo_max_height

    if logos is not None:
        logos_count = logos.count()
        logos_combined_width = (logo_width * logos_count) + (
            logo_spacing * (logos_count - 1)
        )
        logo_x = (page_width - logos_combined_width) / 2
        logos_reserved_space = 0

        for logo in logos:
            logo_proportion = logo.file.width / logo.file.height
            logo_height = logo_width / logo_proportion
            logo_absolute_url = request.build_absolute_uri(logo.file.url)
            certificate.drawImage(
                logo_absolute_url,
                logo_x,
                470,
                width=logo_width,
                height=logo_height,
                mask="auto",
            )
            logo_x += logo_width + logo_spacing

    # Header
    certificate.setFont("Times-Roman", 30, leading=None)
    certificate.drawCentredString(
        395, 390 + logos_reserved_space, str(certificate_title).upper(), charSpace=4.5
    )

    certificate.setFont("Times-Roman", 18, leading=None)
    certificate.drawCentredString(
        395, 330 + logos_reserved_space / 2, str(certificate_presented_to)
    )

    # Learner info
    certificate.setFont("Times-Bold", 42, leading=None)
    certificate.drawCentredString(
        395, 264 + logos_reserved_space / 2, f"{user.first_name} {user.last_name}"
    )

    # Course info
    certificate.setFont("Times-Roman", 18, leading=None)
    certificate.drawCentredString(
        395,
        210 + logos_reserved_space / 2,
        f"{certificate_for_completing} {course_type_name}",
    )
    certificate.setFont("Times-Italic", 26, leading=None)
    course_name = textwrap.wrap(certificate_term, width=60)
    course_name_position = 160 + logos_reserved_space / 2
    for line in course_name:
        certificate.drawCentredString(395, course_name_position, line)
        course_name_position = course_name_position - 30

    # Footer
    certificate.setFont("Helvetica", 12, leading=None)
    certificate.drawCentredString(395, 60, f"{certificate_generated_on} {date}")

    # Close the PDF object cleanly, and we're done.
    certificate.showPage()
    certificate.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=secure_filename(filename))
