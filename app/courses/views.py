import io
import textwrap

# from datetime import datetime
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas

from GEN.decorators import course_enrollment_check
from GEN.support_methods import enrollment_test
from core.views import check_is_instructor
from courses.support_methods import requirement_fulfilled, section_mark_completed
from .models import Course, Section, SectionItem, Status
from content.models import ContentItem, MatchColumnsItem, MatchColumnsGame
from videos.models import VideoFile
from .progress import progress

not_enrolled_error = _("You are not enrolled in the requested course.")


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, MatchColumnsItem):
            return 'BLABLA'
        return super().default(obj)


@login_required
@course_enrollment_check(enrollment_test)
def course(request, pk):
    course_object = get_object_or_404(Course, pk=pk)
    sections = course_object.sections.filter(published=True)
    discussions = course_object.discussions.all()
    quizzes = course_object.quizzes.all()
    # TODO: improve this: I've hardcoded this section name because info isn't a dynamic section item
    section_name = "Info"

    # create status object for course and sections, if they don't exist
    # TODO: this should only be done on first access
    for section in sections:
        if section.published:
            Status.objects.get_or_create(
                learner=request.user,
                course=course_object,
                section=section
            )
    course_object.status.get_or_create(
        learner=request.user,
        course=course_object,
        section=None
    )

    # progress status
    discussions_progress = progress(request.user, discussions)
    quizzes_progress = progress(request.user, quizzes)
    sections_progress = progress(request.user, sections)

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
        section_items = SectionItem.objects.filter(section=section_object, published=True)

        for item in section_items:
            try:
                item.__getattribute__("videofile")
                item.type = 'Video'
            except VideoFile.DoesNotExist:
                pass

            try:
                item.__getattribute__("contentitem")
                item.type = 'Content'
            except ContentItem.DoesNotExist:
                pass

            if item.type == 'Content':
                try:
                    # section.game = True if section.matchcolumnsgame else False
                    item.contentitem.__getattribute__("matchcolumnsgame")
                    item.game = True
                    item.game_info_json = serialize('json', [item.contentitem.matchcolumnsgame])
                    item.game_source_items_json = serialize('json',
                                                            item.contentitem.matchcolumnsgame.source_column_items.all())
                    item.game_choice1_items_json = serialize('json',
                                                             item.contentitem.matchcolumnsgame.choice1_column_items.all())
                    item.game_choice2_items_json = serialize('json',
                                                             item.contentitem.matchcolumnsgame.choice2_column_items.all())
                except:
                    item.game = False
                    # game_info_json = None
                    # game_source_items_json = None
                    # game_choice1_items_json = None
                    # game_choice2_items_json = None

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
            # "game_info_json": game_info_json,
            # "game_source_items_json": game_source_items_json,
            # "game_choice1_items_json": game_choice1_items_json,
            # "game_choice2_items_json": game_choice2_items_json,
        },
    )


@login_required
@course_enrollment_check(enrollment_test)
def generate_certificate(request, pk):
    course_object = get_object_or_404(Course, pk=pk)
    user = request.user
    sections_statuses = Status.objects.filter(learner=user, course=course_object)
    filename = f'GEN - {course_object.code} - {request.user.first_name} {request.user.last_name}.pdf'
    date = timezone.localtime().isoformat()

    sections_completed = []
    for item in sections_statuses:
        sections_completed.append(item.completed)

    if all(sections_completed):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        certificate = canvas.Canvas(buffer, pagesize=landscape(letter))
        certificate.setTitle('Certificate')

        # Header
        certificate.setFont('Helvetica', 40, leading=None)
        certificate.drawCentredString(415, 500, 'Certificate of Conclusion')
        certificate.drawCentredString(415, 450, 'Certificat de Conclusion')
        certificate.setFont('Helvetica', 24, leading=None)
        certificate.drawCentredString(415, 370, 'This certificate is presented to / Ce certificat est présenté à')

        # Learner info
        certificate.setFont('Helvetica-Bold', 36, leading=None)
        certificate.drawCentredString(415, 320, f'{user.first_name} {user.last_name}')

        # Course info
        certificate.setFont('Helvetica', 24, leading=None)
        certificate.drawCentredString(415, 270, 'for completing the following / for completing the following')

        certificate.setFont('Helvetica-Oblique', 20, leading=None)
        course_name = textwrap.wrap(course_object.name, width=70)
        course_name_position = 220
        for line in course_name:
            certificate.drawCentredString(415, course_name_position, line)
            course_name_position = course_name_position - 30

        # Footer
        certificate.setFont('Helvetica', 12, leading=None)
        certificate.drawCentredString(415, 50, f'Generated on / Généré le: {date}')

        # Close the PDF object cleanly, and we're done.
        certificate.showPage()
        certificate.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=filename)
    else:
        messages.warning(
            request,
            _("You have not completed this course yet.")
        )
        return redirect("course", pk=course_object.pk)
