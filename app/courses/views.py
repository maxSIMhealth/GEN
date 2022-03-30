import io
import textwrap

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas

from GEN.decorators import course_enrollment_check, check_requirement, check_permission
from GEN.support_methods import enrollment_test
from core.support_methods import filter_by_access_restriction, check_is_instructor
from courses.support_methods import course_mark_completed, section_mark_completed, progress
from games.models import MoveToColumnsGroup
from .models import Course, Section, SectionItem, Status, CERTIFICATE_COURSE
from werkzeug.utils import secure_filename

not_enrolled_error = _('You are not enrolled in the requested course.')
certificate_title = _('Certificate of Completion')
certificate_presented_to = _('This certificate is presented to')
certificate_for_completing = _('for completing the')
certificate_generated_on = _('Generated on')


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
                learner=user,
                course=course_object,
                section=section
            )
    course_object.status.get_or_create(
        learner=user,
        course=course_object,
        section=None
    )

    # progress status
    discussions_progress = progress(request.user, course_object, discussions)
    quizzes_progress = progress(request.user, course_object, quizzes)
    sections_progress = progress(request.user, course_object, sections)
    course_completed = True if sections_progress['current'] == sections_progress['max'] else False

    # FIXME: implement proper course grouping
    last_course_object = user.member.last()
    if course_object == last_course_object:
        last_course = True
    else:
        last_course = False

    if course_completed:
        message_congratulations = _(f"Congratulations, you have completed this {course_type}.")
        if not last_course:
            message_congratulations += _(f"\nPlease go to the Home page to access the next {course_type}.")
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


@login_required
@course_enrollment_check(enrollment_test)
@check_permission("section")
@check_requirement()
def section_page(request, pk, section_pk):
    user = request.user
    course_object = get_object_or_404(Course, pk=pk)
    section_object = get_object_or_404(Section, pk=section_pk)
    section_items = section_object.section_items.filter(published=True)
    section_items = filter_by_access_restriction(course_object, section_items, user)
    gamification = course_object.enable_gamification
    allow_submission_list = []
    allow_submission = False
    start_date_reached = False
    end_date_passed = False
    section_status, section_status_created = Status.objects.get_or_create(
        learner=request.user,
        course=course_object,
        section=section_object
    )

    # check if the current section is the last one
    last_section_object = course_object.sections.last()
    if section_object == last_section_object:
        last_section = True
    else:
        last_section = False

    # sets congratulations message, if the section is completed
    if section_status.completed:
        message_congratulations = _("Congratulations! You have completed this section.")
        if section_object.final_assessment:
            message_congratulations = _("Congratulations! You have passed the assessment.")
        if not last_section:
            message_congratulations += _("\nPlease navigate to the next section.")
        else:
            if course_object.provide_certificate:
                message_congratulations += _("\nYour certificate of completion is now available in the Information section.")
    else:
        message_congratulations = None

    if request.method == "POST":
        # TODO: check section type and set completed status based on its contents

        # if last section, set course status entry as completed
        if last_section:
            course_mark_completed(request, course_object)
        else:
            section_mark_completed(request, section_object)

        my_kwargs = dict(
            pk=course_object.pk,
            section_pk=section_object.pk
        )

        return redirect("section", **my_kwargs)

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

    if section_object.section_type == "Q":
        if section_object.group_by_video:
            section_items = section_items
            section_template = "sections/section_quiz_grouped.html"
        else:
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
        section_items = SectionItem.objects.filter(section=section_object, published=True)

        for item in section_items:
            if hasattr(item, "videofile"):
                item.type = 'Video'
            elif hasattr(item, "contentitem"):
                item.type = 'Content'
            elif hasattr(item, 'game'):
                item.type = 'Game'
                if item.game.type == 'MC':
                    # get 'move to column' game elements
                    game_elements = MoveToColumnsGroup.objects.filter(game=item)[0]
                    item.game.info_json = serialize('json', [game_elements])
                    item.game.source_items_json = serialize('json', game_elements.source_items.all())
                    item.game.choice1_items_json = serialize('json', game_elements.choice1_items.all())
                    item.game.choice2_items_json = serialize('json', game_elements.choice2_items.all())
                elif item.game.type == 'TB':
                    # 'text boxes' game
                    item.game.terms = serialize('json', item.game.textboxesterm_set.all())
                    item.game.items = serialize('json', item.game.textboxesitem_set.all())
                elif item.game.type == 'MT':
                    # 'match terms' game
                    item.game.terms = serialize('json', item.game.textboxesterm_set.all())
                    item.game.items = serialize('json', item.game.textboxesitem_set.all())
            else:
                item.type = None

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
        filename = f'GEN - {course_object.code} - {request.user.first_name} {request.user.last_name}.pdf'
        certificate_template = course_object.certificate_template
        date = timezone.localtime().isoformat()

        sections_completed = []
        for item in sections_statuses:
            sections_completed.append(item.completed)

        if all(sections_completed):
            return render_certificate_pdf(course_object, date, filename, certificate_template, request, user)
        else:
            messages.warning(
                request,
                _("You have not completed this course/module yet.")
            )
            return redirect("course", pk=course_object.pk)
    else:
        messages.warning(
            request,
            _("This course/module does not provide a certificate of conclusion.")
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
    if (template is None):
        logos = None
        frame = None
    else:
        frame = template.frame
        logos = template.logos.all()
        if (logos.count() == 0):
            logos = None

    # Page
    page_width = landscape(letter)[0]
    page_height = landscape(letter)[1]

    # Frame
    if (frame is not None):
        frame_absolute_url = request.build_absolute_uri(frame.file.url)
        certificate.drawImage(frame_absolute_url, 0, 0, width=page_width, height=page_height)

    # Logos
    # The preferred logo size 200 x 80 points.
    # Width is fixed at 200 and height is automatically calculated while maintaining proportion.
    logo_spacing = 20
    logo_width = 200
    logo_max_height = 80
    logos_reserved_space = logo_max_height

    if (logos is not None):
        logos_count = logos.count()
        logos_combined_width = (logo_width * logos_count) + (logo_spacing * (logos_count - 1))
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
                mask='auto'
            )
            logo_x += (logo_width + logo_spacing)

    # Header
    certificate.setFont('Times-Roman', 30, leading=None)
    certificate.drawCentredString(395, 390 + logos_reserved_space, str(certificate_title).upper(), charSpace=4.5)

    certificate.setFont('Times-Roman', 18, leading=None)
    certificate.drawCentredString(395, 330 + logos_reserved_space / 2, str(certificate_presented_to))

    # Learner info
    certificate.setFont('Times-Bold', 42, leading=None)
    certificate.drawCentredString(395, 264 + logos_reserved_space / 2, f'{user.first_name} {user.last_name}')

    # Course info
    certificate.setFont('Times-Roman', 18, leading=None)
    certificate.drawCentredString(395, 210 + logos_reserved_space / 2, f'{certificate_for_completing} {course_type_name}')
    certificate.setFont('Times-Italic', 26, leading=None)
    course_name = textwrap.wrap(certificate_term, width=60)
    course_name_position = 160 + logos_reserved_space / 2
    for line in course_name:
        certificate.drawCentredString(395, course_name_position, line)
        course_name_position = course_name_position - 30

    # Footer
    certificate.setFont('Helvetica', 12, leading=None)
    certificate.drawCentredString(395, 60, f'{certificate_generated_on} {date}')

    # Close the PDF object cleanly, and we're done.
    certificate.showPage()
    certificate.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=secure_filename(filename))
