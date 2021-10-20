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
from core.models import CertificateLogoFile
from core.support_methods import filter_by_access_restriction, check_is_instructor
from courses.support_methods import section_mark_completed, progress
from games.models import MoveToColumnsGroup
from .models import Course, Section, SectionItem, Status

not_enrolled_error = _("You are not enrolled in the requested course.")


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
    # TODO: improve this: I've hardcoded this section name because info isn't a dynamic section item
    section_name = "Information"

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

    return render(
        request,
        "sections/section_info.html",
        {
            "course": course_object,
            "course_completed": course_completed,
            "section_name": section_name,
            "discussions_progress": discussions_progress,
            "quizzes_progress": quizzes_progress,
            "sections_progress": sections_progress
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

    if request.method == "POST":
        # TODO: check section type and set completed status based on its contents

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
            "gamification": gamification,
            "allow_submission": allow_submission,
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
        logos = CertificateLogoFile.objects.all()
        date = timezone.localtime().isoformat()

        sections_completed = []
        for item in sections_statuses:
            sections_completed.append(item.completed)

        if all(sections_completed):
            return render_certificate_pdf(course_object, date, filename, logos, request, user)
        else:
            messages.warning(
                request,
                _("You have not completed this course yet.")
            )
            return redirect("course", pk=course_object.pk)
    else:
        messages.warning(
            request,
            _("This course does not provide a certificate of conclusion.")
        )
        return redirect("course", pk=course_object.pk)


def render_certificate_pdf(course_object, date, filename, logos, request, user):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    # Create the PDF object, using the buffer as its "file."
    certificate = canvas.Canvas(buffer, pagesize=landscape(letter))
    certificate.setTitle('Certificate of Conclusion')
    # Logos
    # The preferred logo size 200 x 80 points.
    # Width is fixed at 200 and height is automatically calculated while maintaining proportion.
    logo_spacing = 20
    logo_width = 200
    logo_max_height = 80
    page_width = landscape(letter)[0]
    logos_count = logos.count()
    logos_combined_width = (logo_width * logos_count) + (logo_spacing * (logos_count - 1))
    logo_x = (page_width - logos_combined_width) / 2
    logos_reserved_space = logo_max_height if logos_count == 0 else 0
    for logo in logos:
        logo_proportion = logo.file.width / logo.file.height
        logo_height = logo_width / logo_proportion
        logo_absolute_url = request.build_absolute_uri(logo.file.url)
        certificate.drawImage(
            logo_absolute_url,
            logo_x,
            490,
            width=logo_width,
            height=logo_height,
            mask='auto'
        )
        logo_x += (logo_width + logo_spacing)
    # Header
    certificate.setFont('Helvetica', 40, leading=None)
    certificate.drawCentredString(395, 420 + logos_reserved_space, 'Certificate of Conclusion')
    certificate.drawCentredString(395, 370 + logos_reserved_space, 'Certificat de Conclusion')
    certificate.setFont('Helvetica', 24, leading=None)
    certificate.drawCentredString(395, 320 + logos_reserved_space,
                                  'This certificate is presented to / Ce certificat est présenté à')
    # Learner info
    certificate.setFont('Helvetica-Bold', 36, leading=None)
    certificate.drawCentredString(395, 270 + logos_reserved_space / 2, f'{user.first_name} {user.last_name}')
    # Course info
    certificate.setFont('Helvetica', 24, leading=None)
    certificate.drawCentredString(395, 220, 'for completing the following / pour avoir complété ce qui suit')
    certificate.setFont('Helvetica-Oblique', 20, leading=None)
    course_name = textwrap.wrap(course_object.name, width=70)
    course_name_position = 170
    for line in course_name:
        certificate.drawCentredString(395, course_name_position, line)
        course_name_position = course_name_position - 30
    # Footer
    certificate.setFont('Helvetica', 12, leading=None)
    certificate.drawCentredString(395, 50, f'Generated on / Généré le: {date}')
    # Close the PDF object cleanly, and we're done.
    certificate.showPage()
    certificate.save()
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=filename)
