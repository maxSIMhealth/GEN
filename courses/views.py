from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Course, Section, SectionItem
from .progress import progress


@login_required
def course(request, pk):
    course_object = get_object_or_404(Course, pk=pk)
    forums = course_object.forums.all()
    quizzes = course_object.quizzes.all()

    # progress status
    forums_progress = progress(request, forums)
    quizzes_progress = progress(request, quizzes)

    return render(
        request,
        "course.html",
        {
            "course": course_object,
            "forums_progress": forums_progress,
            "quizzes_progress": quizzes_progress,
        },
    )


@login_required
def section_page(request, pk, section_pk):
    course_object = get_object_or_404(Course, pk=pk)
    section_object = get_object_or_404(Section, pk=section_pk)

    # section_types = Section.SECTION_TYPES

    if section_object.section_type == "Q":
        section_template = "section_quiz.html"
    elif section_object.section_type == "D":
        section_template = "section_discussion.html"

    return render(
        request,
        section_template,
        {"course": course_object, "current_section": section_object},
    )
