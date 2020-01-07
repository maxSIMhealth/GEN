from django.shortcuts import render, get_object_or_404

from .models import Course
from .progress import progress
from GEN import settings


def course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    forums = course.forums.all()
    quizzes = course.quizzes.all()
    gamification = False

    # progress status
    forums_progress = progress(request, forums)
    quizzes_progress = progress(request, quizzes)

    if settings.GAMIFICATION:
        gamification = True

    return render(request, 'course.html', {'course': course, 'forums_progress': forums_progress, 'quizzes_progress': quizzes_progress, 'gamification': gamification})
