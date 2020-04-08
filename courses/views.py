from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from GEN import settings
from .models import Course
from .progress import progress


@login_required
def course(request, pk):
    course_object = get_object_or_404(Course, pk=pk)
    forums = course_object.forums.all()
    quizzes = course_object.quizzes.all()
    gamification = False

    # progress status
    forums_progress = progress(request, forums)
    quizzes_progress = progress(request, quizzes)

    if settings.GAMIFICATION:
        gamification = True

    return render(request, 'course.html',
                  {'course': course_object,
                   'forums_progress': forums_progress,
                   'quizzes_progress': quizzes_progress,
                   'gamification': gamification})
