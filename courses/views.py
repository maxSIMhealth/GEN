from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Course, Section, SectionItem
from .progress import progress


@login_required
def course(request, pk):
    course_object = get_object_or_404(Course, pk=pk)
    sections = course_object.sections.filter(published=True)
    discussions = course_object.discussions.all()
    quizzes = course_object.quizzes.all()

    # progress status
    discussions_progress = progress(request, discussions)
    quizzes_progress = progress(request, quizzes)

    return render(
        request,
        "course.html",
        {
            "course": course_object,
            "sections": sections,
            "discussions_progress": discussions_progress,
            "quizzes_progress": quizzes_progress,
        },
    )


@login_required
def section_page(request, pk, section_pk):
    course_object = get_object_or_404(Course, pk=pk)
    section_object = get_object_or_404(Section, pk=section_pk)
    section_items = section_object.section_items.filter(published=True)
    gamification = course_object.enable_gamification

    # section_types = Section.SECTION_TYPES

    if section_object.section_type == "Q":
        section_template = "section_quiz.html"
    elif section_object.section_type == "D":
        section_template = "section_discussion.html"
    elif section_object.section_type == "V":
        section_template = "section_videos.html"
    elif section_object.section_type == "U":
        section_template = "section_upload.html"
        section_items = section_items.filter(author=request.user)

    return render(
        request,
        section_template,
        {
            "course": course_object,
            "section": section_object,
            "section_items": section_items,
            "gamification": gamification,
        },
    )
